"""Unit tests for user profile service."""

import unittest

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.services.user_profile_service import UserProfileError, UserProfileService


class FakeUserRepository:
    """In-memory user repository for user profile service tests."""

    def __init__(self):
        """Initialize users."""
        self._users = {
            1: User(
                id=1,
                first_name="Ada",
                last_name="Lovelace",
                email="ada@example.com",
                password_hash="hash",
                created_at="now",
            )
        }

    def find_by_id(self, user_id: int) -> User | None:
        """Return user by id."""
        return self._users.get(user_id)


class FakeProjectRepository:
    """In-memory project repository for user profile service tests."""

    def list_projects_for_user(self, user_id: int) -> list[Project]:
        """Return projects for user."""
        if user_id != 1:
            return []
        return [
            Project(
                id=10,
                name="Alpha",
                created_by_user_id=1,
                created_at="now",
            )
        ]


class FakeTaskRepository:
    """In-memory task repository for user profile service tests."""

    def list_all_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return tasks for user."""
        if user_id != 1:
            return []
        return [
            Task(
                id=20,
                title="Task",
                description="Description",
                created_by_user_id=1,
                created_at="now",
            )
        ]


class TestUserProfileService(unittest.TestCase):
    """Tests for user profile data collection."""

    def setUp(self):
        """Create service with fake repositories."""
        self.service = UserProfileService(
            FakeUserRepository(),
            FakeProjectRepository(),
            FakeTaskRepository(),
        )

    def test_get_profile_returns_user_projects_and_tasks(self):
        """Profile should contain user data, projects, and task participation."""
        profile = self.service.get_profile(1)

        self.assertEqual(profile.user.email, "ada@example.com")
        self.assertEqual(profile.projects[0].name, "Alpha")
        self.assertEqual(profile.tasks[0].title, "Task")

    def test_get_profile_requires_existing_user(self):
        """Missing user id and unknown user should fail."""
        with self.assertRaises(UserProfileError):
            self.service.get_profile(None)

        with self.assertRaises(UserProfileError):
            self.service.get_profile(999)


if __name__ == "__main__":
    unittest.main()
