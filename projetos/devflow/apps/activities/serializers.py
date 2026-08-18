from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer
from apps.activities.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "task",
            "actor",
            "verb",
            "field",
            "old_value",
            "new_value",
            "created_at",
        )
        read_only_fields = fields
