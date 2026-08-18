from django.contrib import admin

from apps.activities.models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("task", "actor", "verb", "field", "created_at")
    list_filter = ("verb",)
