from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.core.permissions import require_role
from apps.workspaces import services
from apps.workspaces.models import Workspace, WorkspaceMembership
from apps.workspaces.serializers import MembershipSerializer, WorkspaceSerializer

Role = WorkspaceMembership.Role


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer

    def get_queryset(self) -> QuerySet[Workspace]:
        return (
            Workspace.objects.filter(memberships__user=self.request.user)
            .select_related("created_by")
            .distinct()
        )

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workspace = services.create_workspace(
            name=serializer.validated_data["name"],
            slug=serializer.validated_data.get("slug") or None,
            owner=request.user,
        )
        return Response(
            self.get_serializer(workspace).data, status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer: WorkspaceSerializer) -> None:
        require_role(self.request.user, serializer.instance, Role.ADMIN)
        serializer.save()

    def perform_destroy(self, instance: Workspace) -> None:
        require_role(self.request.user, instance, Role.ADMIN)
        instance.delete()  # soft delete


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    filterset_fields = ("workspace", "role")

    def get_queryset(self) -> QuerySet[WorkspaceMembership]:
        return (
            WorkspaceMembership.objects.filter(
                workspace__memberships__user=self.request.user
            )
            .select_related("user", "workspace")
            .distinct()
        )

    def perform_create(self, serializer: MembershipSerializer) -> None:
        require_role(
            self.request.user, serializer.validated_data["workspace"], Role.ADMIN
        )
        serializer.save()

    def perform_update(self, serializer: MembershipSerializer) -> None:
        require_role(self.request.user, serializer.instance.workspace, Role.ADMIN)
        serializer.save()

    def perform_destroy(self, instance: WorkspaceMembership) -> None:
        # Admin remove qualquer membro; o próprio usuário pode sair.
        if instance.user_id != self.request.user.id:
            require_role(self.request.user, instance.workspace, Role.ADMIN)
        instance.delete()
