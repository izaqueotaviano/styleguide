"""Testes da service layer e das permissões básicas.

Rodar com: python manage.py test --settings=config.settings.test
"""
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.activities.models import Activity
from apps.notifications.models import Notification
from apps.projects.services import create_project
from apps.tasks import services
from apps.workspaces.models import Workspace, WorkspaceMembership
from apps.workspaces.services import add_member, create_workspace


class TaskServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.alice = User.objects.create_user(
            "alice", email="alice@example.com", password="x"
        )
        cls.bob = User.objects.create_user("bob", email="bob@example.com", password="x")
        cls.workspace = create_workspace(name="Acme", owner=cls.alice)
        add_member(workspace=cls.workspace, user=cls.bob)
        cls.project = create_project(
            workspace=cls.workspace, created_by=cls.alice, name="Core", key="CORE"
        )

    def test_create_task_assigns_sequential_numbers_and_defaults(self) -> None:
        t1 = services.create_task(project=self.project, author=self.alice, title="Uma")
        t2 = services.create_task(project=self.project, author=self.alice, title="Duas")
        self.assertEqual((t1.number, t2.number), (1, 2))
        self.assertEqual(t1.key, "CORE-1")
        self.assertEqual(t1.status.name, "Backlog")
        self.assertTrue(
            t1.activities.filter(verb=Activity.Verb.CREATED).exists()
        )

    def test_move_task_to_done_sets_completed_at(self) -> None:
        task = services.create_task(project=self.project, author=self.alice, title="X")
        done = self.project.statuses.get(name="Done")
        task = services.move_task(
            task=task, actor=self.alice, changes={"status": done}
        )
        self.assertIsNotNone(task.completed_at)
        self.assertTrue(
            task.activities.filter(verb=Activity.Verb.STATUS_CHANGED).exists()
        )
        backlog = self.project.statuses.get(name="Backlog")
        task = services.move_task(
            task=task, actor=self.alice, changes={"status": backlog}
        )
        self.assertIsNone(task.completed_at)

    def test_move_task_inserts_at_position(self) -> None:
        t1 = services.create_task(project=self.project, author=self.alice, title="A")
        t2 = services.create_task(project=self.project, author=self.alice, title="B")
        t3 = services.create_task(project=self.project, author=self.alice, title="C")
        backlog = self.project.statuses.get(name="Backlog")

        # Insere C no topo da coluna: A e B são deslocadas.
        services.move_task(
            task=t3, actor=self.alice, changes={"status": backlog, "order": 0}
        )
        t1.refresh_from_db(); t2.refresh_from_db(); t3.refresh_from_db()
        self.assertEqual(t3.order, 0)
        self.assertEqual((t1.order, t2.order), (1, 1))

        # Insere B logo antes de A.
        services.move_task(
            task=t2, actor=self.alice, changes={"status": backlog, "order": t1.order}
        )
        t1.refresh_from_db(); t2.refresh_from_db(); t3.refresh_from_db()
        ordering = sorted(
            [t1, t2, t3], key=lambda task: (task.order, task.created_at)
        )
        self.assertEqual([task.title for task in ordering], ["C", "B", "A"])

    def test_assign_task_notifies_assignee(self) -> None:
        task = services.create_task(project=self.project, author=self.alice, title="X")
        services.assign_task(task=task, actor=self.alice, assignee=self.bob)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.bob, verb=Notification.Verb.TASK_ASSIGNED, task=task
            ).exists()
        )
        self.assertTrue(task.activities.filter(verb=Activity.Verb.ASSIGNED).exists())

    def test_comment_resolves_mentions_and_notifies(self) -> None:
        task = services.create_task(project=self.project, author=self.alice, title="X")
        comment = services.add_comment(
            task=task, author=self.alice, body="Olha isso, @bob!"
        )
        self.assertIn(self.bob, comment.mentions.all())
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.bob, verb=Notification.Verb.MENTIONED, comment=comment
            ).exists()
        )

    def test_subtasks_limited_to_one_level(self) -> None:
        parent = services.create_task(
            project=self.project, author=self.alice, title="Pai"
        )
        child = services.create_task(
            project=self.project, author=self.alice, title="Filha", parent=parent
        )
        with self.assertRaises(ValidationError):
            services.create_task(
                project=self.project, author=self.alice, title="Neta", parent=child
            )

    def test_status_from_another_project_is_rejected(self) -> None:
        other = create_project(
            workspace=self.workspace, created_by=self.alice, name="Web", key="WEB"
        )
        wrong_status = other.statuses.first()
        with self.assertRaises(ValidationError):
            services.create_task(
                project=self.project,
                author=self.alice,
                title="X",
                status=wrong_status,
            )


class TaskAPIPermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_user(
            "admin", email="admin@example.com", password="x"
        )
        cls.guest = User.objects.create_user(
            "guest", email="guest@example.com", password="x"
        )
        cls.outsider = User.objects.create_user(
            "outsider", email="outsider@example.com", password="x"
        )
        cls.workspace = create_workspace(name="Acme", owner=cls.admin)
        add_member(
            workspace=cls.workspace,
            user=cls.guest,
            role=WorkspaceMembership.Role.GUEST,
        )
        cls.project = create_project(
            workspace=cls.workspace, created_by=cls.admin, name="Core", key="CORE"
        )
        cls.task = services.create_task(
            project=cls.project, author=cls.admin, title="Tarefa"
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_guest_cannot_create_task(self) -> None:
        self.client.force_authenticate(self.guest)
        response = self.client.post(
            "/api/v1/tasks/",
            {"project": str(self.project.id), "title": "Nova"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_guest_can_read_and_comment(self) -> None:
        self.client.force_authenticate(self.guest)
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        response = self.client.post(
            "/api/v1/comments/",
            {"task": str(self.task.id), "body": "Posso comentar!"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_outsider_sees_nothing(self) -> None:
        self.client.force_authenticate(self.outsider)
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_member_can_create_and_move_task(self) -> None:
        member = User.objects.create_user(
            "member", email="member@example.com", password="x"
        )
        add_member(workspace=self.workspace, user=member)
        self.client.force_authenticate(member)
        response = self.client.post(
            "/api/v1/tasks/",
            {"project": str(self.project.id), "title": "Do member", "type": "bug"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["key"], "CORE-2")
        done = self.project.statuses.get(name="Done")
        response = self.client.post(
            f"/api/v1/tasks/{response.data['id']}/move/",
            {"status": str(done.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"]["category"], "completed")


class SeedDemoCommandTestCase(TestCase):
    def test_seed_demo_creates_data_and_is_idempotent(self) -> None:
        call_command("seed_demo")
        call_command("seed_demo")  # segunda execução não duplica nada
        self.assertEqual(Workspace.objects.filter(slug="demo").count(), 1)
        demo_workspace = Workspace.objects.get(slug="demo")
        project = demo_workspace.projects.get(key="CORE")
        self.assertEqual(project.tasks.count(), 5)
        self.assertTrue(
            project.tasks.filter(status__name="In Progress").exists()
        )
        self.assertEqual(project.sections.count(), 2)
        self.assertEqual(demo_workspace.labels.count(), 2)
