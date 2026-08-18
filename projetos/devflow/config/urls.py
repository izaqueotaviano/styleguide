"""Rotas da API (v1)."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import MeView, RegisterView, UserSearchView
from apps.activities.views import ActivityViewSet
from apps.notifications.views import NotificationViewSet
from apps.projects.views import (
    LabelViewSet,
    ProjectViewSet,
    SectionViewSet,
    TaskStatusViewSet,
)
from apps.tasks.views import CommentViewSet, TaskViewSet
from apps.workspaces.views import MembershipViewSet, WorkspaceViewSet

router = DefaultRouter()
router.register("workspaces", WorkspaceViewSet, basename="workspace")
router.register("memberships", MembershipViewSet, basename="membership")
router.register("projects", ProjectViewSet, basename="project")
router.register("statuses", TaskStatusViewSet, basename="status")
router.register("sections", SectionViewSet, basename="section")
router.register("labels", LabelViewSet, basename="label")
router.register("tasks", TaskViewSet, basename="task")
router.register("comments", CommentViewSet, basename="comment")
router.register("activities", ActivityViewSet, basename="activity")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/register/", RegisterView.as_view(), name="register"),
    path("api/v1/me/", MeView.as_view(), name="me"),
    path("api/v1/users/", UserSearchView.as_view(), name="user-search"),
    path("api/v1/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
