from django.contrib import admin

from apps.tasks.models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "title",
        "project",
        "type",
        "priority",
        "status",
        "assignee",
        "deleted_at",
    )
    list_filter = ("type", "priority")
    search_fields = ("title",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at", "deleted_at")
