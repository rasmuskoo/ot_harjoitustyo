"""Unit tests for project service."""

import unittest

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.services.project_service import (
    ProjectCreationError,
    ProjectService,
    ProjectTaskError,
)


class FakeProjectRepository:
    """In-memory project repository for project service tests."""

    def __init__(self):
        """Initialize empty project storage."""
        self._projects: dict[int, Project] = {}
        self._members: dict[int, list[User]] = {}
        self._tasks: dict[int, list[Task]] = {}
        self._next_id = 1

    def create_project(self, project: Project) -> Project:
        """Store and return project with generated id."""
        stored_project = Project(
            id=self._next_id,
            name=project.name,
            created_by_user_id=project.created_by_user_id,
            created_at=project.created_at,
        )
        self._projects[stored_project.id] = stored_project
        self._members[stored_project.id] = []
        self._tasks[stored_project.id] = []
        self._next_id += 1
        return stored_project

    def add_member(self, project_id: int, user_id: int) -> None:
        """Add lightweight member entry for project."""
        self._members.setdefault(project_id, []).append(
            User(
                id=user_id,
                first_name=f"User{user_id}",
                last_name="Member",
                email=f"user{user_id}@example.com",
                password_hash="hash",
                created_at="now",
            )
        )

    def list_projects_for_user(self, user_id: int) -> list[Project]:
        """Return projects that include the given user."""
        project_ids = [
            project_id
            for project_id, members in self._members.items()
            if any(member.id == user_id for member in members)
        ]
        return [self._projects[project_id] for project_id in project_ids]

    def find_project_for_user(self, project_id: int, user_id: int) -> Project | None:
        """Return project if the given user belongs to it."""
        project = self._projects.get(project_id)
        if project is None:
            return None
        if not any(member.id == user_id for member in self._members.get(project_id, [])):
            return None
        return project

    def list_members(self, project_id: int) -> list[User]:
        """Return stored members for a project."""
        return list(self._members.get(project_id, []))

    def list_tasks(self, project_id: int) -> list[Task]:
        """Return stored tasks for a project."""
        return list(self._tasks.get(project_id, []))


class FakeTaskRepository:
    """In-memory task repository for project service tests."""

    def __init__(self):
        """Initialize empty task storage."""
        self._tasks: dict[int, Task] = {}
        self._participants: dict[int, set[int]] = {}

    def assign_task_to_project_for_user(self, task_id: int, project_id: int, user_id: int) -> bool:
        """Assign task to project when user is participant."""
        task = self._tasks.get(task_id)
        if task is None or user_id not in self._participants.get(task_id, set()):
            return False

        self._tasks[task_id] = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            created_by_user_id=task.created_by_user_id,
            created_at=task.created_at,
            project_id=project_id,
            is_completed=task.is_completed,
        )
        return True

    def add_participants(self, task_id: int, user_ids: list[int]) -> None:
        """Attach many users to task participant list."""
        self._participants.setdefault(task_id, set()).update(user_ids)

    def list_unassigned_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return visible tasks with no project."""
        return [
            task
            for task_id, task in self._tasks.items()
            if user_id in self._participants.get(task_id, set()) and task.project_id is None
        ]


class TestProjectService(unittest.TestCase):
    """Tests for project creation and task assignment."""

    def setUp(self):
        """Create project service with fake repositories."""
        self.project_repository = FakeProjectRepository()
        self.task_repository = FakeTaskRepository()
        self.project_service = ProjectService(self.project_repository, self.task_repository)

    def test_create_project_adds_owner_to_members(self):
        """Project creator should always become a member."""
        project = self.project_service.create_project("Alpha", 1, [2, 3])

        self.assertIsNotNone(project.id)
        member_ids = [member.id for member in self.project_repository.list_members(project.id)]
        self.assertEqual(member_ids, [1, 2, 3])

    def test_create_project_with_empty_name_raises_error(self):
        """Blank project name should fail."""
        with self.assertRaises(ProjectCreationError):
            self.project_service.create_project("   ", 1, [])

    def test_add_existing_task_to_project_adds_all_project_members_as_participants(self):
        """Existing task linked to project should become visible to all project members."""
        project = self.project_service.create_project("Alpha", 1, [2])
        self.task_repository._tasks[5] = Task(
            id=5,
            title="Task",
            description="Description",
            created_by_user_id=1,
            created_at="now",
        )
        self.task_repository._participants[5] = {1}

        self.project_service.add_existing_task_to_project(project.id, 5, 1)

        self.assertEqual(self.task_repository._tasks[5].project_id, project.id)
        self.assertEqual(self.task_repository._participants[5], {1, 2})

    def test_get_project_details_requires_membership(self):
        """Project details should be restricted to members."""
        project = self.project_service.create_project("Alpha", 1, [])

        with self.assertRaises(ProjectTaskError):
            self.project_service.get_project_details(project.id, 2)


if __name__ == "__main__":
    unittest.main()
