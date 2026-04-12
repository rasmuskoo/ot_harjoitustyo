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
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._participants: dict[int, set[int]] = {}
        self._next_id = 1

    def create_task(self, task: Task) -> Task:
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
        self._participants.setdefault(task_id, set()).add(user_id)

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if user_id not in self._participants.get(task_id, set()):
            return None
        return task

    def update_task_for_user(self, task_id: int, user_id: int, title: str, description: str) -> bool:
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
        task = self.find_task_for_user(task_id, user_id)
        if task is None:
            return False

        del self._tasks[task_id]
        self._participants.pop(task_id, None)
        return True


class TestTaskService(unittest.TestCase):
    def setUp(self):
        self.task_repository = FakeTaskRepository()
        self.task_service = TaskService(self.task_repository)

    def test_create_task_success(self):
        task = self.task_service.create_task("Header", "Description", 1)

        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "Header")
        self.assertEqual(task.description, "Description")

    def test_create_task_with_empty_header_raises_error(self):
        with self.assertRaises(TaskCreationError):
            self.task_service.create_task("", "Description", 1)

    def test_edit_task_success(self):
        created_task = self.task_service.create_task("Old", "Old desc", 1)

        updated_task = self.task_service.edit_task(created_task.id, 1, "New", "New desc")

        self.assertEqual(updated_task.title, "New")
        self.assertEqual(updated_task.description, "New desc")

    def test_edit_task_not_found_raises_error(self):
        with self.assertRaises(TaskEditError):
            self.task_service.edit_task(999, 1, "New", "New desc")

    def test_complete_task_success(self):
        created_task = self.task_service.create_task("Header", "Description", 1)

        self.task_service.complete_task(created_task.id, 1)

        updated_task = self.task_repository.find_task_for_user(created_task.id, 1)
        self.assertIsNotNone(updated_task)
        self.assertTrue(updated_task.is_completed)

    def test_complete_task_already_completed_raises_error(self):
        created_task = self.task_service.create_task("Header", "Description", 1)
        self.task_service.complete_task(created_task.id, 1)

        with self.assertRaises(TaskCompleteError):
            self.task_service.complete_task(created_task.id, 1)

    def test_delete_task_success(self):
        created_task = self.task_service.create_task("Header", "Description", 1)

        self.task_service.delete_task(created_task.id, 1)

        deleted_task = self.task_repository.find_task_for_user(created_task.id, 1)
        self.assertIsNone(deleted_task)

    def test_delete_task_not_found_raises_error(self):
        with self.assertRaises(TaskDeleteError):
            self.task_service.delete_task(999, 1)


if __name__ == "__main__":
    unittest.main()
