"""Integration tests for SQLite repositories."""

from pathlib import Path
import tempfile
import unittest

from src.entities.label import Label
from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories import database
from src.repositories.label_repository import LabelRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository


class RepositoryTestCase(unittest.TestCase):
    """Base class that points repositories to an isolated temporary database."""

    def setUp(self):
        """Create temporary database and repository instances."""
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self._temporary_directory.name) / "test.sqlite"
        database.initialize_database()

        self.user_repository = UserRepository()
        self.task_repository = TaskRepository()
        self.project_repository = ProjectRepository()
        self.label_repository = LabelRepository()

    def tearDown(self):
        """Restore database path and remove temporary directory."""
        database.DATABASE_PATH = self._original_database_path
        self._temporary_directory.cleanup()

    def _create_user(self, email: str = "ada@example.com") -> User:
        """Create a stored user for repository tests."""
        return self.user_repository.create_user(
            User(
                first_name="Ada",
                last_name="Lovelace",
                email=email,
                password_hash="hash",
                created_at="now",
            )
        )

    def _create_task(self, user_id: int, title: str = "Task") -> Task:
        """Create a stored task and attach user as participant."""
        task = self.task_repository.create_task(
            Task(
                title=title,
                description="Description",
                created_by_user_id=user_id,
                created_at="now",
                priority="high",
                due_date="2026-05-01",
            )
        )
        self.task_repository.add_participant(task.id, user_id)
        return task

    def _create_project(self, user_id: int, name: str = "Project") -> Project:
        """Create a stored project and attach user as member."""
        project = self.project_repository.create_project(
            Project(
                name=name,
                created_by_user_id=user_id,
                created_at="now",
                priority="low",
                due_date="2026-06-01",
            )
        )
        self.project_repository.add_member(project.id, user_id)
        return project


class TestDatabaseInitialization(RepositoryTestCase):
    """Tests for database initialization and migration helpers."""

    def test_initialize_database_creates_expected_tables(self):
        """Database initialization should create application tables."""
        with database.get_database_connection() as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()

        table_names = {row[0] for row in rows}
        self.assertIn("users", table_names)
        self.assertIn("tasks", table_names)
        self.assertIn("projects", table_names)
        self.assertIn("labels", table_names)
        self.assertIn("task_labels", table_names)


class TestUserRepository(RepositoryTestCase):
    """Tests for user repository."""

    def test_create_find_and_list_users(self):
        """User repository should create, find, and list users."""
        created_user = self._create_user()

        found_user = self.user_repository.find_by_email("ada@example.com")
        users = self.user_repository.list_users()

        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(users[0].email, "ada@example.com")

    def test_find_by_email_returns_none_when_user_missing(self):
        """Unknown email lookup should return none."""
        self.assertIsNone(self.user_repository.find_by_email("missing@example.com"))


class TestTaskRepository(RepositoryTestCase):
    """Tests for task repository."""

    def test_task_lifecycle_for_user(self):
        """Task repository should support task listing, updating, completing, and deleting."""
        user = self._create_user()
        task = self._create_task(user.id)

        active_tasks = self.task_repository.list_tasks_for_user(user.id)
        self.assertEqual(active_tasks[0].priority, "high")
        self.assertEqual(active_tasks[0].due_date, "2026-05-01")

        was_updated = self.task_repository.update_task_for_user(
            task.id,
            user.id,
            "Updated",
            "Updated description",
        )
        updated_task = self.task_repository.find_task_for_user(task.id, user.id)
        self.assertTrue(was_updated)
        self.assertEqual(updated_task.title, "Updated")

        was_completed = self.task_repository.complete_task_for_user(task.id, user.id)
        completed_tasks = self.task_repository.list_completed_tasks_for_user(user.id)
        self.assertTrue(was_completed)
        self.assertEqual(completed_tasks[0].id, task.id)

        was_deleted = self.task_repository.delete_task_for_user(task.id, user.id)
        self.assertTrue(was_deleted)
        self.assertIsNone(self.task_repository.find_task_for_user(task.id, user.id))

    def test_task_permission_checks_return_false_or_none(self):
        """Task operations should fail when user is not a participant."""
        owner = self._create_user("owner@example.com")
        other = self._create_user("other@example.com")
        task = self._create_task(owner.id)

        self.assertIsNone(self.task_repository.find_task_for_user(task.id, other.id))
        self.assertFalse(
            self.task_repository.update_task_for_user(task.id, other.id, "New", "New desc")
        )
        self.assertFalse(self.task_repository.complete_task_for_user(task.id, other.id))
        self.assertFalse(self.task_repository.delete_task_for_user(task.id, other.id))

    def test_assign_and_list_unassigned_project_tasks(self):
        """Task repository should assign visible unassigned tasks to projects."""
        user = self._create_user()
        project = self._create_project(user.id)
        task = self._create_task(user.id)

        unassigned_tasks = self.task_repository.list_unassigned_tasks_for_user(user.id)
        self.assertEqual(unassigned_tasks[0].id, task.id)

        was_assigned = self.task_repository.assign_task_to_project_for_user(
            task.id,
            project.id,
            user.id,
        )
        assigned_task = self.task_repository.find_task_for_user(task.id, user.id)

        self.assertTrue(was_assigned)
        self.assertEqual(assigned_task.project_id, project.id)
        self.assertEqual(self.task_repository.list_unassigned_tasks_for_user(user.id), [])

    def test_add_participants_ignores_empty_list(self):
        """Adding no participants should be a no-op."""
        self.task_repository.add_participants(999, [])


class TestProjectRepository(RepositoryTestCase):
    """Tests for project repository."""

    def test_project_lifecycle_for_creator(self):
        """Project repository should create, list, find, and delete creator project."""
        user = self._create_user()
        project = self._create_project(user.id)
        task = self._create_task(user.id)
        self.task_repository.assign_task_to_project_for_user(task.id, project.id, user.id)

        projects = self.project_repository.list_projects_for_user(user.id)
        found_project = self.project_repository.find_project_for_user(project.id, user.id)
        members = self.project_repository.list_members(project.id)
        tasks = self.project_repository.list_tasks(project.id)

        self.assertEqual(projects[0].priority, "low")
        self.assertEqual(found_project.due_date, "2026-06-01")
        self.assertEqual(members[0].id, user.id)
        self.assertEqual(tasks[0].id, task.id)

        was_deleted = self.project_repository.delete_project_for_user(project.id, user.id)
        unlinked_task = self.task_repository.find_task_for_user(task.id, user.id)
        self.assertTrue(was_deleted)
        self.assertIsNone(
            self.project_repository.find_project_for_user(project.id, user.id)
        )
        self.assertIsNone(unlinked_task.project_id)

    def test_project_delete_requires_creator(self):
        """Non-creator should not be able to delete project."""
        owner = self._create_user("owner@example.com")
        other = self._create_user("other@example.com")
        project = self._create_project(owner.id)
        self.project_repository.add_member(project.id, other.id)

        self.assertFalse(self.project_repository.delete_project_for_user(project.id, other.id))


class TestLabelRepository(RepositoryTestCase):
    """Tests for label repository."""

    def test_label_repository_operations(self):
        """Label repository should create, find, search, attach, and list labels."""
        user = self._create_user()
        task = self._create_task(user.id)
        label = self.label_repository.create_label(Label(name="frontend"))

        found_by_name = self.label_repository.find_by_name("frontend")
        found_by_id = self.label_repository.find_by_id(label.id)
        labels = self.label_repository.list_labels()
        searched_labels = self.label_repository.search_labels("front")
        self.label_repository.add_label_to_task(task.id, label.id)
        task_labels = self.label_repository.list_labels_for_task(task.id)

        self.assertEqual(found_by_name.id, label.id)
        self.assertEqual(found_by_id.name, "frontend")
        self.assertEqual(labels[0].name, "frontend")
        self.assertEqual(searched_labels[0].id, label.id)
        self.assertEqual(task_labels[0].name, "frontend")

    def test_label_find_methods_return_none_when_missing(self):
        """Missing label lookups should return none."""
        self.assertIsNone(self.label_repository.find_by_name("missing"))
        self.assertIsNone(self.label_repository.find_by_id(999))


if __name__ == "__main__":
    unittest.main()
