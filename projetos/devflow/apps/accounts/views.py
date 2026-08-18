from django.db.models import Q
from rest_framework import generics, permissions

from apps.accounts.models import User
from apps.accounts.serializers import RegisterSerializer, UserSummarySerializer


class MeView(generics.RetrieveAPIView):
    """Dados do usuário autenticado."""

    serializer_class = UserSummarySerializer

    def get_object(self) -> User:
        return self.request.user


class RegisterView(generics.CreateAPIView):
    """Cadastro simples de usuário (aberto)."""

    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class UserSearchView(generics.ListAPIView):
    """Busca usuários por username/e-mail (para convidar ao workspace)."""

    serializer_class = UserSummarySerializer
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get("search", "").strip()
        if len(query) < 2:
            return User.objects.none()
        return User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).order_by("username")[:10]
