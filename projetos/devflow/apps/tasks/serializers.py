from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSummarySerializer
from apps.projects.models import Label, Section, TaskStatus
from apps.projects.serializers import LabelSerializer
from apps.tasks.models import Comment, Task


class TaskStatusMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ("id", "name", "category")
        read_only_fields = fields


class SectionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "name", "order")
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    """Representação de leitura de uma tarefa."""

    key = serializers.CharField(read_only=True)
    status = TaskStatusMiniSerializer(read_only=True)
    section = SectionMiniSerializer(read_only=True)
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "key",
            "number",
            "project",
            "parent",
            "title",
            "description",
            "type",
            "priority",
            "status",
            "section",
            "assignee",
            "reviewer",
            "labels",
            "estimate",
            "due_date",
            "order",
            "completed_at",
            "subtasks_count",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_subtasks_count(self, obj: Task) -> int:
        return obj.subtasks.count()


class TaskDetailSerializer(TaskSerializer):
    subtasks = TaskSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ("subtasks",)
        read_only_fields = fields


class TaskWriteSerializer(serializers.ModelSerializer):
    """Entrada de criação/edição. As validações de consistência entre
    projeto/status/seção/membros ficam na service layer."""

    labels = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Label.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = (
            "project",
            "parent",
            "title",
            "description",
            "type",
            "priority",
            "status",
            "section",
            "assignee",
            "reviewer",
            "labels",
            "estimate",
            "due_date",
            "order",
        )
        extra_kwargs = {"status": {"required": False}}


class MoveTaskSerializer(serializers.Serializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(), required=False
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), required=False, allow_null=True
    )
    order = serializers.IntegerField(required=False, min_value=0)


class AssignTaskSerializer(serializers.Serializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True
    )


class CommentSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    mentions = UserSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "task", "author", "body", "mentions", "created_at", "updated_at")
        read_only_fields = ("id", "author", "mentions", "created_at", "updated_at")
