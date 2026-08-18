from django.contrib import admin

from apps.projects.models import Label, Project, Section, TaskStatus


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "workspace", "created_at", "deleted_at")
    search_fields = ("name", "key")


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "category", "order", "is_default")
    list_filter = ("category",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "order")


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "color")
