"""Registro de activities."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db import models

from apps.accounts.models import User
from apps.activities.models import Activity


def serialize_value(value: Any) -> Any:
    """Converte um valor de campo em algo serializável no JSONField."""
    if value is None:
        return None
    if isinstance(value, models.Model):
        return {"id": str(value.pk), "label": str(value)}
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def log_activity(
    *,
    task: "models.Model",
    actor: User | None,
    verb: str,
    field: str = "",
    old_value: Any = None,
    new_value: Any = None,
) -> Activity:
    """Cria um evento no histórico da tarefa."""
    return Activity.objects.create(
        task=task,
        actor=actor,
        verb=verb,
        field=field,
        old_value=serialize_value(old_value),
        new_value=serialize_value(new_value),
    )
