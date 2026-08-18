"""Histórico de mudanças (activity log) por tarefa."""
from __future__ import annotations

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class Activity(TimeStampedUUIDModel):
    """Evento imutável no histórico de uma tarefa.

    ``verb`` diz o que aconteceu; para mudanças de campo genéricas,
    ``field`` + ``old_value``/``new_value`` guardam o diff em JSON.
    """

    class Verb(models.TextChoices):
        CREATED = "created", "criou a tarefa"
        UPDATED = "updated", "atualizou um campo"
        STATUS_CHANGED = "status_changed", "mudou o status"
        SECTION_CHANGED = "section_changed", "moveu de seção"
        ASSIGNED = "assigned", "alterou o responsável"
        COMMENTED = "commented", "comentou"
        DELETED = "deleted", "excluiu a tarefa"

    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="activities"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="activities",
    )
    verb = models.CharField(max_length=20, choices=Verb.choices)
    field = models.CharField(max_length=40, blank=True)
    old_value = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    new_value = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "activities"
        indexes = [models.Index(fields=["task", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.actor} {self.get_verb_display()} ({self.task_id})"
