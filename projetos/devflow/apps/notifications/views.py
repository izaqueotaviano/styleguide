from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet[Notification]:
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related("actor", "task", "task__project")
        if self.request.query_params.get("unread") in ("1", "true"):
            queryset = queryset.filter(read_at__isnull=True)
        return queryset

    @action(detail=True, methods=["post"])
    def read(self, request: Request, pk: str | None = None) -> Response:
        notification = self.get_object()
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at", "updated_at"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request: Request) -> Response:
        updated = Notification.objects.filter(
            recipient=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
        return Response({"marked_read": updated})
