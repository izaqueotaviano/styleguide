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
