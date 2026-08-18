from django.db.models import QuerySet
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.permissions import require_member, require_role
from apps.tasks import services
from apps.tasks.filters import TaskFilter
from apps.tasks.models import Comment, Task
from apps.tasks.serializers import (
    AssignTaskSerializer,
    CommentSerializer,
    MoveTaskSerializer,
    TaskDetailSerializer,
    TaskSerializer,
    TaskWriteSerializer,
)
from apps.workspaces.models import EDITOR_ROLES, WorkspaceMembership

Role = WorkspaceMembership.Role


class TaskViewSet(viewsets.ModelViewSet):
    filterset_class = TaskFilter
    search_fields = ("title", "description")
    ordering_fields = ("order", "created_at", "updated_at", "due_date", "priority")

    def get_queryset(self) -> QuerySet[Task]:
        return (
            Task.objects.filter(
                project__workspace__memberships__user=self.request.user
            )
            .select_related(
                "project", "status", "section", "assignee", "reviewer", "created_by"
            )
            .prefetch_related("labels")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer

    # -- Escrita: valida entrada, checa papel e delega ao service. ---------

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        project = data.pop("project")
        require_role(request.user, project.workspace, *EDITOR_ROLES)
        task = services.create_task(project=project, author=request.user, **data)
        return Response(
            TaskSerializer(task).data, status=http_status.HTTP_201_CREATED
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        task = self.get_object()
        require_role(request.user, task.project.workspace, *EDITOR_ROLES)
        serializer = TaskWriteSerializer(task, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        task = services.update_task(
            task=task, actor=request.user, changes=dict(serializer.validated_data)
        )
        return Response(TaskSerializer(task).data)

    def perform_destroy(self, instance: Task) -> None:
        require_role(self.request.user, instance.project.workspace, *EDITOR_ROLES)
        services.delete_task(task=instance, actor=self.request.user)

    # -- Ações de domínio ---------------------------------------------------

    @action(detail=False, methods=["get"], url_path="my")
    def my_tasks(self, request: Request) -> Response:
        """My Tasks: tudo que está atribuído ao usuário autenticado."""
        queryset = self.filter_queryset(
            self.get_queryset().filter(assignee=request.user)
        )
        page = self.paginate_queryset(queryset)
        serializer = TaskSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["post"])
    def move(self, request: Request, pk: str | None = None) -> Response:
        task = self.get_object()
        require_role(request.user, task.project.workspace, *EDITOR_ROLES)
        serializer = MoveTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = services.move_task(
            task=task, actor=request.user, changes=dict(serializer.validated_data)
        )
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"])
    def assign(self, request: Request, pk: str | None = None) -> Response:
        task = self.get_object()
        require_role(request.user, task.project.workspace, *EDITOR_ROLES)
        serializer = AssignTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = services.assign_task(
            task=task,
            actor=request.user,
            assignee=serializer.validated_data["assignee"],
        )
        return Response(TaskSerializer(task).data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    filterset_fields = ("task",)

    def get_queryset(self) -> QuerySet[Comment]:
        return (
            Comment.objects.filter(
                task__project__workspace__memberships__user=self.request.user
            )
            .select_related("author", "task")
            .prefetch_related("mentions")
            .distinct()
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data["task"]
        # Guests também podem comentar — basta ser membro.
        require_member(request.user, task.project.workspace)
        comment = services.add_comment(
            task=task, author=request.user, body=serializer.validated_data["body"]
        )
        return Response(
            self.get_serializer(comment).data, status=http_status.HTTP_201_CREATED
        )

    def perform_update(self, serializer: CommentSerializer) -> None:
        comment = serializer.instance
        if comment.author_id != self.request.user.id:
            raise PermissionDenied("Apenas o autor pode editar o comentário.")
        serializer.save(task=comment.task)

    def perform_destroy(self, instance: Comment) -> None:
        if instance.author_id != self.request.user.id:
            require_role(
                self.request.user, instance.task.project.workspace, Role.ADMIN
            )
        instance.delete()  # soft delete
