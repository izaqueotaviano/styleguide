"""Projetos, status configuráveis, seções do board e labels."""
from __future__ import annotations

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedUUIDModel
from apps.workspaces.models import Workspace


class Project(TimeStampedUUIDModel, SoftDeleteModel):
    """Projeto dentro de um workspace.

    ``key`` é o prefixo das tarefas (ex.: "ENG" → ENG-42) e
    ``next_task_number`` guarda o contador sequencial por projeto,
    incrementado com lock na service layer.
    """

    class EstimateUnit(models.TextChoices):
        POINTS = "points", "Story points"
        HOURS = "hours", "Horas"

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=120)
    key = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                r"^[A-Z][A-Z0-9]{1,9}$",
                "Use 2 a 10 caracteres maiúsculos (letras e números), começando por letra.",
            )
        ],
        help_text="Prefixo das tarefas, ex.: ENG → ENG-42.",
    )
    description = models.TextField(blank=True)
    estimate_unit = models.CharField(
        max_length=10, choices=EstimateUnit.choices, default=EstimateUnit.POINTS
    )
    next_task_number = models.PositiveIntegerField(default=0, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_projects",
    )

    class Meta:
        ordering = ("name",)
        base_manager_name = "all_objects"
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "key"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_project_key_per_workspace_alive",
            )
        ]

    def __str__(self) -> str:
        return f"{self.key} · {self.name}"


class TaskStatus(TimeStampedUUIDModel):
    """Status configurável por projeto.

    A ``category`` dá semântica estável para o sistema (métricas,
    ``completed_at``, filtros de board), enquanto ``name`` e ``order``
    ficam livres para cada time customizar.
    """

    class Category(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        UNSTARTED = "unstarted", "A fazer"
        STARTED = "started", "Em andamento"
        COMPLETED = "completed", "Concluído"
        CANCELED = "canceled", "Cancelado"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="statuses"
    )
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=12, choices=Category.choices)
    order = models.PositiveSmallIntegerField(default=0)
    is_default = models.BooleanField(
        default=False, help_text="Status inicial das tarefas criadas sem status."
    )

    class Meta:
        ordering = ("order", "created_at")
        verbose_name_plural = "task statuses"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="uniq_status_name_per_project"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Section(TimeStampedUUIDModel, SoftDeleteModel):
    """Agrupamento visual de tarefas no board/list (ex.: 'Sprint 12')."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "created_at")
        base_manager_name = "all_objects"

    def __str__(self) -> str:
        return self.name


class Label(TimeStampedUUIDModel):
    """Label reutilizável entre projetos do mesmo workspace."""

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="labels"
    )
    name = models.CharField(max_length=60)
    color = models.CharField(
        max_length=7,
        default="#6B7280",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use um hex como #22C55E.")],
    )

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "name"], name="uniq_label_name_per_workspace"
            )
        ]

    def __str__(self) -> str:
        return self.name
