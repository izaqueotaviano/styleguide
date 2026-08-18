"""Criação de notificações."""
from __future__ import annotations

from typing import TYPE_CHECKING

from apps.accounts.models import User
from apps.notifications.models import Notification

if TYPE_CHECKING:  # pragma: no cover
    from apps.tasks.models import Comment, Task


def notify(
    *,
    recipient: User,
    actor: User | None,
    verb: str,
    task: "Task | None" = None,
    comment: "Comment | None" = None,
) -> Notification | None:
    """Cria uma notificação, ignorando auto-notificações."""
    if actor is not None and recipient.pk == actor.pk:
        return None
    return Notification.objects.create(
        recipient=recipient, actor=actor, verb=verb, task=task, comment=comment
    )
