from django.db.models import ProtectedError, QuerySet
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.permissions import require_role
from apps.projects import services
from apps.projects.models import Label, Project, Section, TaskStatus
from apps.projects.serializers import (
    LabelSerializer,
    ProjectSerializer,
    SectionSerializer,
    TaskStatusSerializer,
)
from apps.workspaces.models import EDITOR_ROLES, WorkspaceMembership

Role = WorkspaceMembership.Role


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filterset_fields = ("workspace",)
    search_fields = ("name", "key")

    def get_queryset(self) -> QuerySet[Project]:
        return (
            Project.objects.filter(workspace__memberships__user=self.request.user)
            .select_related("workspace", "created_by")
            .distinct()
        )

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        require_role(request.user, data["workspace"], *EDITOR_ROLES)
        project = services.create_project(
            workspace=data["workspace"],
            created_by=request.user,
            name=data["name"],
            key=data["key"],
            description=data.get("description", ""),
            estimate_unit=data.get("estimate_unit", Project.EstimateUnit.POINTS),
        )
        return Response(
            self.get_serializer(project).data, status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer: ProjectSerializer) -> None:
        require_role(self.request.user, serializer.instance.workspace, *EDITOR_ROLES)
        # O projeto não muda de workspace depois de criado.
        serializer.save(workspace=serializer.instance.workspace)

    def perform_destroy(self, instance: Project) -> None:
        require_role(self.request.user, instance.workspace, Role.ADMIN)
        instance.delete()  # soft delete


class TaskStatusViewSet(viewsets.ModelViewSet):
    """Configuração do fluxo de status — restrita a admins."""

    serializer_class = TaskStatusSerializer
    filterset_fields = ("project",)

    def get_queryset(self) -> QuerySet[TaskStatus]:
        return (
            TaskStatus.objects.filter(
                project__workspace__memberships__user=self.request.user
            )
            .select_related("project")
            .distinct()
        )

    def perform_create(self, serializer: TaskStatusSerializer) -> None:
        require_role(
            self.request.user,
            serializer.validated_data["project"].workspace,
            Role.ADMIN,
        )
        serializer.save()

    def perform_update(self, serializer: TaskStatusSerializer) -> None:
        require_role(self.request.user, serializer.instance.project.workspace, Role.ADMIN)
        serializer.save(project=serializer.instance.project)

    def perform_destroy(self, instance: TaskStatus) -> None:
        require_role(self.request.user, instance.project.workspace, Role.ADMIN)
        try:
            instance.delete()
        except ProtectedError as exc:
            raise ValidationError(
                "Não é possível excluir um status que ainda possui tarefas."
            ) from exc


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    filterset_fields = ("project",)

    def get_queryset(self) -> QuerySet[Section]:
        return (
            Section.objects.filter(
                project__workspace__memberships__user=self.request.user
            )
            .select_related("project")
            .distinct()
        )

    def perform_create(self, serializer: SectionSerializer) -> None:
        require_role(
            self.request.user,
            serializer.validated_data["project"].workspace,
            *EDITOR_ROLES,
        )
        serializer.save()

    def perform_update(self, serializer: SectionSerializer) -> None:
        require_role(
            self.request.user, serializer.instance.project.workspace, *EDITOR_ROLES
        )
        serializer.save(project=serializer.instance.project)

    def perform_destroy(self, instance: Section) -> None:
        require_role(self.request.user, instance.project.workspace, *EDITOR_ROLES)
        instance.delete()  # soft delete; tasks ficam com section=NULL


class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    filterset_fields = ("workspace",)

    def get_queryset(self) -> QuerySet[Label]:
        return (
            Label.objects.filter(workspace__memberships__user=self.request.user)
            .select_related("workspace")
            .distinct()
        )

    def perform_create(self, serializer: LabelSerializer) -> None:
        require_role(
            self.request.user, serializer.validated_data["workspace"], *EDITOR_ROLES
        )
        serializer.save()

    def perform_update(self, serializer: LabelSerializer) -> None:
        require_role(self.request.user, serializer.instance.workspace, *EDITOR_ROLES)
        serializer.save(workspace=serializer.instance.workspace)

    def perform_destroy(self, instance: Label) -> None:
        require_role(self.request.user, instance.workspace, *EDITOR_ROLES)
        instance.delete()
