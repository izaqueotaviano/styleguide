"""Regras de negócio de projetos."""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import User
from apps.projects.models import Project, TaskStatus
from apps.workspaces.models import Workspace

#: Fluxo padrão criado junto com cada projeto (nome, categoria, is_default).
DEFAULT_STATUSES: tuple[tuple[str, str, bool], ...] = (
    ("Backlog", TaskStatus.Category.BACKLOG, True),
    ("Todo", TaskStatus.Category.UNSTARTED, False),
    ("In Progress", TaskStatus.Category.STARTED, False),
    ("In Review", TaskStatus.Category.STARTED, False),
    ("Done", TaskStatus.Category.COMPLETED, False),
    ("Canceled", TaskStatus.Category.CANCELED, False),
)


@transaction.atomic
def create_project(
    *,
    workspace: Workspace,
    created_by: User,
    name: str,
    key: str,
    description: str = "",
    estimate_unit: str = Project.EstimateUnit.POINTS,
) -> Project:
    """Cria o projeto já com o fluxo de status padrão."""
    key = key.upper()
    if Project.objects.filter(workspace=workspace, key=key).exists():
        raise ValidationError({"key": "Já existe um projeto com esta chave no workspace."})
    project = Project.objects.create(
        workspace=workspace,
        name=name,
        key=key,
        description=description,
        estimate_unit=estimate_unit,
        created_by=created_by,
    )
    TaskStatus.objects.bulk_create(
        TaskStatus(
            project=project, name=name_, category=category, order=order, is_default=default
        )
        for order, (name_, category, default) in enumerate(DEFAULT_STATUSES)
    )
    return project
