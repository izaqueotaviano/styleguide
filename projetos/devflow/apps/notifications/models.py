"""Notificações in-app básicas."""
from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class Notification(TimeStampedUUIDModel):
    class Verb(models.TextChoices):
        TASK_ASSIGNED = "task_assigned", "atribuiu uma tarefa a você"
        REVIEW_REQUESTED = "review_requested", "pediu sua revisão"
        MENTIONED = "mentioned", "mencionou você"
        COMMENTED = "commented", "comentou em uma tarefa sua"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    verb = models.CharField(max_length=20, choices=Verb.choices)
    task = models.ForeignKey(
        "tasks.Task", null=True, blank=True, on_delete=models.CASCADE, related_name="+"
    )
    comment = models.ForeignKey(
        "tasks.Comment",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["recipient", "read_at"])]

    def __str__(self) -> str:
        return f"{self.recipient} ← {self.get_verb_display()}"
