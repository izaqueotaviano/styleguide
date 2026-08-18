"""Regras de negócio de workspaces e membros."""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from apps.accounts.models import User
from apps.workspaces.models import Workspace, WorkspaceMembership


def _unique_slug(name: str) -> str:
    base = slugify(name)[:50] or "workspace"
    slug = base
    suffix = 2
    while Workspace.objects.filter(slug=slug).exists():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


@transaction.atomic
def create_workspace(*, name: str, owner: User, slug: str | None = None) -> Workspace:
    """Cria o workspace e registra o criador como Admin."""
    if slug and Workspace.objects.filter(slug=slug).exists():
        raise ValidationError({"slug": "Já existe um workspace com este slug."})
    workspace = Workspace.objects.create(
        name=name, slug=slug or _unique_slug(name), created_by=owner
    )
    WorkspaceMembership.objects.create(
        workspace=workspace, user=owner, role=WorkspaceMembership.Role.ADMIN
    )
    return workspace


def add_member(
    *,
    workspace: Workspace,
    user: User,
    role: str = WorkspaceMembership.Role.MEMBER,
) -> WorkspaceMembership:
    """Adiciona um usuário ao workspace com o papel informado."""
    if WorkspaceMembership.objects.filter(workspace=workspace, user=user).exists():
        raise ValidationError({"user": "Este usuário já é membro do workspace."})
    return WorkspaceMembership.objects.create(workspace=workspace, user=user, role=role)
