"""Unit tests for task service."""

import unittest

from src.entities.task import Task
from src.services.task_service import (
    TaskCompleteError,
    TaskCreationError,
    TaskDeleteError,
    TaskEditError,
    TaskService,
)


class FakeTaskRepository:
    """In-memory task repository for task service tests."""

    def __init__(self):
        """Initialize empty task and participant storage."""
        self._tasks: dict[int, Task] = {}
        self._participants: dict[int, set[int]] = {}
        self._next_id = 1

    def create_task(self, task: Task) -> Task:
        """Store and return task with generated id."""
        task_id = self._next_id
        self._next_id += 1

        stored_task = Task(
            id=task_id,
            title=task.title,
            description=task.description,
            created_by_user_id=task.created_by_user_id,
            created_at=task.created_at,
            is_completed=task.is_completed,
        )
        self._tasks[task_id] = stored_task
        return stored_task

    def add_participant(self, task_id: int, user_id: int) -> None:
        """Attach user to task participant list."""
        self._participants.setdefault(task_id, set()).add(user_id)

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        """Return task if user is participant."""
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if user_id not in self._participants.get(task_id, set()):
            return None
        return task

    def update_task_for_user(
        self,
        task_id: int,
        user_id: int,
        title: str,
        description: str,
    ) -> bool:
        """Update task title and description for participant."""
        task = self.find_task_for_user(task_id, user_id)
        if task is None:
            return False

        self._tasks[task_id] = Task(
            id=task.id,
            title=title,
            description=description,
            created_by_user_id=task.created_by_user_id,
            created_at=task.created_at,
            is_completed=task.is_completed,
        )
        return True

    def complete_task_for_user(self, task_id: int, user_id: int) -> bool:
        """Mark task completed for participant."""
        task = self.find_task_for_user(task_id, user_id)
        if task is None or task.is_completed:
            return False

        self._tasks[task_id] = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            created_by_user_id=task.created_by_user_id,
            created_at=task.created_at,
            is_completed=True,
        )
        return True

    def delete_task_for_user(self, task_id: int, user_id: int) -> bool:
        """Delete task for participant."""
        task = self.find_task_for_user(task_id, user_id)
        if task is None:
            return False

        del self._tasks[task_id]
        self._participants.pop(task_id, None)
        return True


class TestTaskService(unittest.TestCase):
    """Tests for task creation, editing, completion, and deletion."""

    def setUp(self):
        """Create task service with fake repository."""
        self.task_repository = FakeTaskRepository()
        self.task_service = TaskService(self.task_repository)

    def test_create_task_success(self):
        """Task creation should succeed with valid input."""
        task = self.task_service.create_task("Header", "Description", 1)

        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "Header")
        self.assertEqual(task.description, "Description")

    def test_create_task_with_empty_header_raises_error(self):
        """Empty header should fail task creation."""
        with self.assertRaises(TaskCreationError):
            self.task_service.create_task("", "Description", 1)

    def test_edit_task_success(self):
        """Task edit should update title and description."""
        created_task = self.task_service.create_task("Old", "Old desc", 1)

        updated_task = self.task_service.edit_task(created_task.id, 1, "New", "New desc")

        self.assertEqual(updated_task.title, "New")
        self.assertEqual(updated_task.description, "New desc")

    def test_edit_task_not_found_raises_error(self):
        """Editing unknown task should fail."""
        with self.assertRaises(TaskEditError):
            self.task_service.edit_task(999, 1, "New", "New desc")

    def test_complete_task_success(self):
        """Task completion should mark task as completed."""
        created_task = self.task_service.create_task("Header", "Description", 1)

        self.task_service.complete_task(created_task.id, 1)

        updated_task = self.task_repository.find_task_for_user(created_task.id, 1)
        self.assertIsNotNone(updated_task)
        self.assertTrue(updated_task.is_completed)

    def test_complete_task_already_completed_raises_error(self):
        """Completing already completed task should fail."""
        created_task = self.task_service.create_task("Header", "Description", 1)
        self.task_service.complete_task(created_task.id, 1)

        with self.assertRaises(TaskCompleteError):
            self.task_service.complete_task(created_task.id, 1)

    def test_delete_task_success(self):
        """Task deletion should remove task from repository."""
        created_task = self.task_service.create_task("Header", "Description", 1)

        self.task_service.delete_task(created_task.id, 1)

        deleted_task = self.task_repository.find_task_for_user(created_task.id, 1)
        self.assertIsNone(deleted_task)

    def test_delete_task_not_found_raises_error(self):
        """Deleting unknown task should fail."""
        with self.assertRaises(TaskDeleteError):
            self.task_service.delete_task(999, 1)


if __name__ == "__main__":
    unittest.main()
