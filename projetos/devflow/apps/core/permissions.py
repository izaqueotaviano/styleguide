"""Autorização baseada no papel do usuário dentro do workspace.

Em vez de espalhar ``BasePermission`` complexas por todos os ViewSets,
usamos duas camadas simples:

1. Escopo de queryset — todo ``get_queryset`` filtra pelos workspaces
   dos quais o usuário é membro (nada de fora vaza, nem em listagens).
2. Helpers explícitos (``require_member`` / ``require_role``) chamados
   nos pontos de escrita, que levantam ``PermissionDenied`` (HTTP 403).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.exceptions import PermissionDenied

from apps.workspaces.models import Workspace, WorkspaceMembership

if TYPE_CHECKING:  # pragma: no cover
    from apps.accounts.models import User


def get_membership(user: "User", workspace: Workspace) -> WorkspaceMembership | None:
    """Retorna o vínculo do usuário com o workspace, se existir."""
    if not getattr(user, "is_authenticated", False):
        return None
    return WorkspaceMembership.objects.filter(user=user, workspace=workspace).first()


def require_member(user: "User", workspace: Workspace) -> WorkspaceMembership:
    """Garante que o usuário é membro do workspace (qualquer papel)."""
    membership = get_membership(user, workspace)
    if membership is None:
        raise PermissionDenied("Você não é membro deste workspace.")
    return membership


def require_role(user: "User", workspace: Workspace, *roles: str) -> WorkspaceMembership:
    """Garante que o usuário tem um dos papéis exigidos no workspace."""
    membership = require_member(user, workspace)
    if membership.role not in roles:
        raise PermissionDenied("Seu papel neste workspace não permite esta ação.")
    return membership
