"""Tarefas (issues), subtarefas e comentários."""
from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedUUIDModel
from apps.projects.models import Label, Project, Section, TaskStatus


class Task(TimeStampedUUIDModel, SoftDeleteModel):
    """Unidade central de trabalho.

    Decisões principais:
    - ``number`` é sequencial por projeto (ENG-1, ENG-2, ...), atribuído
      com lock na service layer; a chave legível vem de ``key``.
    - ``status`` é FK para o fluxo configurável do projeto (PROTECT para
      não perder histórico ao apagar um status em uso).
    - Subtarefas: FK ``parent`` limitada a 1 nível de profundidade —
      cobre o MVP sem a complexidade de árvores arbitrárias.
    - ``type`` e ``priority`` são enums fixos (requisito do MVP).
    """

    class Type(models.TextChoices):
        FEATURE = "feature", "Feature"
        BUG = "bug", "Bug"
        IMPROVEMENT = "improvement", "Improvement"
        TECH_DEBT = "tech_debt", "Tech Debt"
        CHORE = "chore", "Chore"

    class Priority(models.TextChoices):
        URGENT = "urgent", "Urgent"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    number = models.PositiveIntegerField(editable=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Markdown.")
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.FEATURE)
    priority = models.CharField(
        max_length=8, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.ForeignKey(TaskStatus, on_delete=models.PROTECT, related_name="tasks")
    section = models.ForeignKey(
        Section, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
    )
    labels = models.ManyToManyField(Label, blank=True, related_name="tasks")
    estimate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Story points ou horas, conforme o estimate_unit do projeto.",
    )
    due_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(
        default=0, help_text="Posição no board/list dentro da seção."
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
    )

    class Meta:
        ordering = ("order", "created_at")
        base_manager_name = "all_objects"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"], name="uniq_task_number_per_project"
            )
        ]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assignee"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.key} {self.title}"

    @property
    def key(self) -> str:
        """Identificador legível, ex.: ENG-42."""
        return f"{self.project.key}-{self.number}"


class Comment(TimeStampedUUIDModel, SoftDeleteModel):
    """Comentário em uma tarefa, com menções via @username."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    body = models.TextField(help_text="Markdown.")
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="mentioned_in_comments"
    )

    class Meta:
        ordering = ("created_at",)
        base_manager_name = "all_objects"

    def __str__(self) -> str:
        return f"Comentário de {self.author} em {self.task_id}"
