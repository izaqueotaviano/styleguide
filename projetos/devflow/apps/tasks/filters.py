"""Filtros da listagem de tarefas."""
import django_filters

from apps.tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    project = django_filters.UUIDFilter(field_name="project_id")
    workspace = django_filters.UUIDFilter(field_name="project__workspace_id")
    status = django_filters.UUIDFilter(field_name="status_id")
    status_category = django_filters.CharFilter(field_name="status__category")
    section = django_filters.UUIDFilter(field_name="section_id")
    assignee = django_filters.NumberFilter(field_name="assignee_id")
    reviewer = django_filters.NumberFilter(field_name="reviewer_id")
    unassigned = django_filters.BooleanFilter(field_name="assignee", lookup_expr="isnull")
    label = django_filters.UUIDFilter(field_name="labels__id")
    parent = django_filters.UUIDFilter(field_name="parent_id")
    top_level = django_filters.BooleanFilter(field_name="parent", lookup_expr="isnull")
    due_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ("type", "priority")
