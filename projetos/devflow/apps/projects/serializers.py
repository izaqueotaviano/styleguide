from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer
from apps.projects.models import Label, Project, Section, TaskStatus


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "workspace",
            "name",
            "key",
            "description",
            "estimate_unit",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_key(self, value: str) -> str:
        return value.upper()

    def validate(self, attrs: dict) -> dict:
        workspace = attrs.get("workspace") or getattr(self.instance, "workspace", None)
        key = attrs.get("key") or getattr(self.instance, "key", None)
        if workspace and key:
            queryset = Project.objects.filter(workspace=workspace, key=key)
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"key": "Já existe um projeto com esta chave no workspace."}
                )
        return attrs


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ("id", "project", "name", "category", "order", "is_default")
        read_only_fields = ("id",)


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "project", "name", "order")
        read_only_fields = ("id",)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ("id", "workspace", "name", "color")
        read_only_fields = ("id",)
