"""Service layer das tarefas — toda regra de negócio importante mora aqui.

As views apenas validam entrada/permissão e delegam para estas funções,
que cuidam de: numeração sequencial, consistência entre projeto/status/
seção/membros, activity log e notificações — sempre dentro de transação.
"""
from __future__ import annotations

import re
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.activities.models import Activity
from apps.activities.services import log_activity, serialize_value
from apps.notifications.models import Notification
from apps.notifications.services import notify
from apps.projects.models import Label, Project, Section, TaskStatus
from apps.tasks.models import Comment, Task
from apps.workspaces.models import WorkspaceMembership

MENTION_PATTERN = re.compile(r"@([\w.+-]+)")

#: Campos rastreados no activity log quando alterados.
TRACKED_FIELDS = (
    "title",
    "description",
    "type",
    "priority",
    "status",
    "section",
    "assignee",
    "reviewer",
    "parent",
    "estimate",
    "due_date",
)


# ---------------------------------------------------------------------------
# Validações de consistência
# ---------------------------------------------------------------------------

def _validate_status(project: Project, status: TaskStatus) -> None:
    if status.project_id != project.id:
        raise ValidationError({"status": "Este status não pertence ao projeto da tarefa."})


def _validate_section(project: Project, section: Section | None) -> None:
    if section is not None and section.project_id != project.id:
        raise ValidationError({"section": "Esta seção não pertence ao projeto da tarefa."})


def _validate_parent(project: Project, parent: Task | None, task: Task | None = None) -> None:
    if parent is None:
        return
    if task is not None and parent.pk == task.pk:
        raise ValidationError({"parent": "Uma tarefa não pode ser subtarefa de si mesma."})
    if parent.project_id != project.id:
        raise ValidationError({"parent": "A tarefa pai precisa ser do mesmo projeto."})
    if parent.parent_id is not None:
        raise ValidationError({"parent": "Subtarefas têm no máximo um nível de profundidade."})


def _validate_member(project: Project, user: User | None, field: str) -> None:
    if user is None:
        return
    is_member = WorkspaceMembership.objects.filter(
        workspace_id=project.workspace_id, user=user
    ).exists()
    if not is_member:
        raise ValidationError({field: "O usuário precisa ser membro do workspace."})


def _validate_labels(project: Project, labels: list[Label]) -> None:
    for label in labels:
        if label.workspace_id != project.workspace_id:
            raise ValidationError({"labels": "Labels precisam pertencer ao mesmo workspace."})


# ---------------------------------------------------------------------------
# Operações
# ---------------------------------------------------------------------------

@transaction.atomic
def create_task(
    *,
    project: Project,
    author: User,
    title: str,
    status: TaskStatus | None = None,
    labels: list[Label] | None = None,
    **fields: Any,
) -> Task:
    """Cria uma tarefa com número sequencial do projeto.

    O ``SELECT ... FOR UPDATE`` no projeto garante que duas criações
    concorrentes nunca recebam o mesmo número.
    """
    project = Project.objects.select_for_update().get(pk=project.pk)
    project.next_task_number += 1
    project.save(update_fields=["next_task_number", "updated_at"])

    if status is None:
        status = (
            project.statuses.filter(is_default=True).first()
            or project.statuses.order_by("order").first()
        )
        if status is None:
            raise ValidationError({"status": "O projeto não possui status configurados."})

    _validate_status(project, status)
    _validate_section(project, fields.get("section"))
    _validate_parent(project, fields.get("parent"))
    _validate_member(project, fields.get("assignee"), "assignee")
    _validate_member(project, fields.get("reviewer"), "reviewer")

    task = Task.objects.create(
        project=project,
        number=project.next_task_number,
        title=title,
        status=status,
        created_by=author,
        **fields,
    )
    if labels:
        _validate_labels(project, labels)
        task.labels.set(labels)

    log_activity(task=task, actor=author, verb=Activity.Verb.CREATED)
    if task.assignee_id:
        notify(
            recipient=task.assignee,
            actor=author,
            verb=Notification.Verb.TASK_ASSIGNED,
            task=task,
        )
    if task.reviewer_id:
        notify(
            recipient=task.reviewer,
            actor=author,
            verb=Notification.Verb.REVIEW_REQUESTED,
            task=task,
        )
    return task


@transaction.atomic
def update_task(*, task: Task, actor: User, changes: dict[str, Any]) -> Task:
    """Aplica mudanças a uma tarefa registrando cada campo alterado."""
    project = task.project
    labels = changes.pop("labels", None)
    changes.pop("project", None)  # tarefa não muda de projeto

    if "status" in changes:
        _validate_status(project, changes["status"])
    if "section" in changes:
        _validate_section(project, changes["section"])
    if "parent" in changes:
        _validate_parent(project, changes["parent"], task=task)
    if "assignee" in changes:
        _validate_member(project, changes["assignee"], "assignee")
    if "reviewer" in changes:
        _validate_member(project, changes["reviewer"], "reviewer")

    changed = False
    for field, new_value in changes.items():
        if field == "order":
            if new_value != task.order:
                task.order = new_value
                changed = True
            continue
        if field not in TRACKED_FIELDS:
            continue
        old_value = getattr(task, field)
        if old_value == new_value:
            continue
        setattr(task, field, new_value)
        changed = True

        if field == "status":
            verb = Activity.Verb.STATUS_CHANGED
            task.completed_at = (
                timezone.now()
                if new_value.category == TaskStatus.Category.COMPLETED
                else None
            )
        elif field == "section":
            verb = Activity.Verb.SECTION_CHANGED
        elif field == "assignee":
            verb = Activity.Verb.ASSIGNED
            if new_value is not None:
                notify(
                    recipient=new_value,
                    actor=actor,
                    verb=Notification.Verb.TASK_ASSIGNED,
                    task=task,
                )
        else:
            verb = Activity.Verb.UPDATED
            if field == "reviewer" and new_value is not None:
                notify(
                    recipient=new_value,
                    actor=actor,
                    verb=Notification.Verb.REVIEW_REQUESTED,
                    task=task,
                )

        log_activity(
            task=task,
            actor=actor,
            verb=verb,
            field=field,
            # Descrição é longa demais para o histórico; guardamos só o diff de metadados.
            old_value=None if field == "description" else serialize_value(old_value),
            new_value=None if field == "description" else serialize_value(new_value),
        )

    if changed:
        task.save()
    if labels is not None:
        _validate_labels(project, labels)
        task.labels.set(labels)
    return task


def move_task(
    *,
    task: Task,
    actor: User,
    changes: dict[str, Any],
) -> Task:
    """Move a tarefa de status/seção e/ou reposiciona no board."""
    allowed = {k: v for k, v in changes.items() if k in ("status", "section", "order")}
    return update_task(task=task, actor=actor, changes=allowed)


def assign_task(*, task: Task, actor: User, assignee: User | None) -> Task:
    """Atribui (ou remove) o responsável pela tarefa."""
    return update_task(task=task, actor=actor, changes={"assignee": assignee})


@transaction.atomic
def add_comment(*, task: Task, author: User, body: str) -> Comment:
    """Cria um comentário, resolve menções e notifica os envolvidos."""
    comment = Comment.objects.create(task=task, author=author, body=body)

    # Menções: apenas usuários que são membros do workspace da tarefa.
    usernames = set(MENTION_PATTERN.findall(body))
    mentioned = list(
        User.objects.filter(
            username__in=usernames,
            workspace_memberships__workspace_id=task.project.workspace_id,
        ).distinct()
    )
    if mentioned:
        comment.mentions.set(mentioned)

    mentioned_ids = {user.pk for user in mentioned}
    for user in mentioned:
        notify(
            recipient=user,
            actor=author,
            verb=Notification.Verb.MENTIONED,
            task=task,
            comment=comment,
        )
    # Envolvidos na tarefa (sem duplicar quem já foi mencionado).
    involved = {task.assignee, task.reviewer, task.created_by} - {None}
    for user in involved:
        if user.pk not in mentioned_ids:
            notify(
                recipient=user,
                actor=author,
                verb=Notification.Verb.COMMENTED,
                task=task,
                comment=comment,
            )

    log_activity(task=task, actor=author, verb=Activity.Verb.COMMENTED)
    return comment


@transaction.atomic
def delete_task(*, task: Task, actor: User) -> None:
    """Soft delete com registro no histórico."""
    log_activity(task=task, actor=actor, verb=Activity.Verb.DELETED)
    task.delete()
