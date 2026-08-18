from django.db.models import QuerySet
from rest_framework import viewsets

from apps.activities.models import Activity
from apps.activities.serializers import ActivitySerializer


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Histórico é imutável: somente leitura via API."""

    serializer_class = ActivitySerializer
    filterset_fields = ("task", "verb")

    def get_queryset(self) -> QuerySet[Activity]:
        return (
            Activity.objects.filter(
                task__project__workspace__memberships__user=self.request.user
            )
            .select_related("actor")
            .distinct()
        )
