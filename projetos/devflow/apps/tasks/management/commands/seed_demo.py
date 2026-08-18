"""Popula dados de demonstração para explorar a API rapidamente.

Uso: python manage.py seed_demo
Idempotente: se o workspace "demo" já existe, não faz nada.
Credenciais criadas: demo / devflow123 (admin) e dev / devflow123.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.projects.services import create_project
from apps.tasks import services as task_services
from apps.tasks.models import Task
from apps.workspaces.models import Workspace
from apps.workspaces.services import add_member, create_workspace


class Command(BaseCommand):
    help = "Cria workspace, projeto e tarefas de demonstração (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        demo, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@devflow.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            demo.set_password("devflow123")
            demo.save(update_fields=["password"])
        dev, created = User.objects.get_or_create(
            username="dev", defaults={"email": "dev@devflow.local"}
        )
        if created:
            dev.set_password("devflow123")
            dev.save(update_fields=["password"])

        if Workspace.objects.filter(slug="demo").exists():
            self.stdout.write("Dados de demonstração já existem — nada a fazer.")
            return

        workspace = create_workspace(name="Demo", owner=demo, slug="demo")
        add_member(workspace=workspace, user=dev)
        project = create_project(
            workspace=workspace,
            created_by=demo,
            name="Core",
            key="CORE",
            description="Projeto de demonstração do DevFlow.",
        )

        login_bug = task_services.create_task(
            project=project,
            author=demo,
            title="Erro 500 ao fazer login com e-mail em maiúsculas",
            description="Reproduzível em produção. Stacktrace no Sentry.",
            type=Task.Type.BUG,
            priority=Task.Priority.URGENT,
            assignee=dev,
        )
        feature = task_services.create_task(
            project=project,
            author=demo,
            title="Board Kanban com drag-and-drop",
            type=Task.Type.FEATURE,
            priority=Task.Priority.HIGH,
            assignee=dev,
            reviewer=demo,
        )
        task_services.create_task(
            project=project,
            author=demo,
            title="Definir colunas do board",
            type=Task.Type.FEATURE,
            parent=feature,
        )
        task_services.create_task(
            project=project,
            author=dev,
            title="Extrair service layer do app de billing",
            type=Task.Type.TECH_DEBT,
            priority=Task.Priority.LOW,
        )
        task_services.create_task(
            project=project,
            author=dev,
            title="Atualizar dependências do CI",
            type=Task.Type.CHORE,
            priority=Task.Priority.MEDIUM,
        )

        in_progress = project.statuses.get(name="In Progress")
        task_services.move_task(
            task=login_bug, actor=dev, changes={"status": in_progress}
        )
        task_services.add_comment(
            task=login_bug,
            author=dev,
            body="Causa raiz encontrada: normalização do e-mail. @demo pode revisar o fix?",
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed concluído! Logins: demo / devflow123 (admin) e dev / devflow123.\n"
                "Explore em /api/docs/ ou /admin/."
            )
        )
