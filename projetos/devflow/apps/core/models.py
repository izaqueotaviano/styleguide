"""Modelos abstratos compartilhados: timestamps, UUID e soft delete."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class TimeStampedUUIDModel(models.Model):
    """Base com chave primária UUID e timestamps automáticos."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet cujo delete() apenas marca os registros como excluídos."""

    def delete(self) -> int:  # type: ignore[override]
        return super().update(deleted_at=timezone.now())

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()


class SoftDeleteManager(models.Manager):
    """Manager padrão: esconde registros soft-deletados."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )


class SoftDeleteModel(models.Model):
    """Base para modelos com exclusão lógica (soft delete).

    - ``objects`` (padrão) esconde registros excluídos — inclusive em
      relacionamentos reversos (``project.tasks`` etc.).
    - ``all_objects`` dá acesso a tudo, incluindo excluídos (usado também
      como base manager para que FKs para registros excluídos não quebrem).
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False) -> None:  # type: ignore[override]
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])
