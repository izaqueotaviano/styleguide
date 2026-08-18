from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)
    task_key = serializers.SerializerMethodField()
    task_title = serializers.SerializerMethodField()
    task_project = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "actor",
            "verb",
            "task",
            "task_key",
            "task_title",
            "task_project",
            "comment",
            "read_at",
            "created_at",
        )
        read_only_fields = fields

    def get_task_key(self, obj: Notification) -> str | None:
        return obj.task.key if obj.task else None

    def get_task_title(self, obj: Notification) -> str | None:
        return obj.task.title if obj.task else None

    def get_task_project(self, obj: Notification) -> str | None:
        return str(obj.task.project_id) if obj.task else None
