from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSummarySerializer
from apps.workspaces.models import Workspace, WorkspaceMembership


class WorkspaceSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)
    created_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Workspace
        fields = ("id", "name", "slug", "created_by", "created_at", "updated_at")
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = WorkspaceMembership
        fields = ("id", "workspace", "user", "user_id", "role", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs: dict) -> dict:
        if self.instance is None:
            workspace = attrs["workspace"]
            user = attrs["user"]
            if WorkspaceMembership.objects.filter(
                workspace=workspace, user=user
            ).exists():
                raise serializers.ValidationError(
                    {"user_id": "Este usuário já é membro do workspace."}
                )
        return attrs
