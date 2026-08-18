"""Workspace (tenant) e vínculo de membros com papéis."""
from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedUUIDModel


class Workspace(TimeStampedUUIDModel, SoftDeleteModel):
    """Unidade de multi-tenancy: tudo no sistema pertence a um workspace."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=60)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_workspaces",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="WorkspaceMembership",
        related_name="workspaces",
    )

    class Meta:
        ordering = ("name",)
        base_manager_name = "all_objects"
        constraints = [
            # Unicidade apenas entre registros "vivos": um slug pode ser
            # reutilizado depois que o workspace original for soft-deletado.
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_workspace_slug_alive",
            )
        ]

    def __str__(self) -> str:
        return self.name


class WorkspaceMembership(TimeStampedUUIDModel):
    """Papel de um usuário dentro de um workspace."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        GUEST = "guest", "Guest"

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user"], name="uniq_workspace_membership"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.workspace} ({self.role})"


#: Papéis com permissão de escrita em projetos/tarefas (Guest fica de fora).
EDITOR_ROLES: tuple[str, str] = (
    WorkspaceMembership.Role.ADMIN,
    WorkspaceMembership.Role.MEMBER,
)
