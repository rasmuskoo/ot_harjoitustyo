"""Unit tests for label service."""

import unittest

from src.entities.label import Label
from src.entities.task import Task
from src.services.label_service import (
    LabelAssignmentError,
    LabelCreationError,
    LabelService,
)


class FakeLabelRepository:
    """In-memory label repository for label service tests."""

    def __init__(self):
        """Initialize empty label storage."""
        self._labels: dict[int, Label] = {}
        self._task_labels: dict[int, set[int]] = {}
        self._next_id = 1

    def create_label(self, label: Label) -> Label:
        """Store and return label with generated id."""
        stored_label = Label(id=self._next_id, name=label.name)
        self._labels[stored_label.id] = stored_label
        self._next_id += 1
        return stored_label

    def find_by_name(self, name: str) -> Label | None:
        """Return stored label by name."""
        return next((label for label in self._labels.values() if label.name == name), None)

    def find_by_id(self, label_id: int) -> Label | None:
        """Return stored label by id."""
        return self._labels.get(label_id)

    def list_labels(self) -> list[Label]:
        """Return labels ordered by name."""
        return sorted(self._labels.values(), key=lambda label: label.name)

    def search_labels(self, query: str) -> list[Label]:
        """Return labels whose names contain query."""
        labels = [label for label in self._labels.values() if query in label.name]
        return sorted(labels, key=lambda label: label.name)

    def add_label_to_task(self, task_id: int, label_id: int) -> None:
        """Attach label id to task id."""
        self._task_labels.setdefault(task_id, set()).add(label_id)

    def list_labels_for_task(self, task_id: int) -> list[Label]:
        """Return labels attached to task."""
        label_ids = self._task_labels.get(task_id, set())
        labels = [self._labels[label_id] for label_id in label_ids]
        return sorted(labels, key=lambda label: label.name)


class FakeTaskRepository:
    """In-memory task repository for label service tests."""

    def __init__(self):
        """Initialize empty task storage."""
        self._tasks: dict[int, Task] = {}
        self._participants: dict[int, set[int]] = {}

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        """Return task when user is participant."""
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if user_id not in self._participants.get(task_id, set()):
            return None
        return task


class TestLabelService(unittest.TestCase):
    """Tests for label creation, searching, and task assignment."""

    def setUp(self):
        """Create label service with fake repositories."""
        self.label_repository = FakeLabelRepository()
        self.task_repository = FakeTaskRepository()
        self.label_service = LabelService(self.label_repository, self.task_repository)

    def test_create_label_success_normalizes_name(self):
        """Label creation should normalize whitespace and case."""
        label = self.label_service.create_label("  Frontend  ")

        self.assertIsNotNone(label.id)
        self.assertEqual(label.name, "frontend")

    def test_create_label_with_empty_name_raises_error(self):
        """Blank label name should fail."""
        with self.assertRaises(LabelCreationError):
            self.label_service.create_label("   ")

    def test_create_duplicate_label_raises_error(self):
        """Duplicate normalized label name should fail."""
        self.label_service.create_label("Backend")

        with self.assertRaises(LabelCreationError):
            self.label_service.create_label(" backend ")

    def test_list_labels_returns_labels_in_name_order(self):
        """Label listing should return labels ordered by name."""
        self.label_service.create_label("beta")
        self.label_service.create_label("alpha")

        labels = self.label_service.list_labels()

        self.assertEqual([label.name for label in labels], ["alpha", "beta"])

    def test_search_labels_returns_matching_labels(self):
        """Label search should return labels matching query."""
        self.label_service.create_label("frontend")
        self.label_service.create_label("backend")

        labels = self.label_service.search_labels("end")

        self.assertEqual([label.name for label in labels], ["backend", "frontend"])

    def test_empty_search_returns_all_labels(self):
        """Empty label search should return all labels."""
        self.label_service.create_label("frontend")
        self.label_service.create_label("backend")

        labels = self.label_service.search_labels("   ")

        self.assertEqual([label.name for label in labels], ["backend", "frontend"])

    def test_add_label_to_task_success(self):
        """Existing label can be attached to task visible to user."""
        label = self.label_service.create_label("frontend")
        self.task_repository._tasks[1] = Task(
            id=1,
            title="Task",
            description="Description",
            created_by_user_id=1,
            created_at="now",
        )
        self.task_repository._participants[1] = {1}

        self.label_service.add_label_to_task(1, label.id, 1)

        labels = self.label_service.list_labels_for_task(1)
        self.assertEqual([stored_label.name for stored_label in labels], ["frontend"])

    def test_add_label_to_task_requires_visible_task(self):
        """Label assignment should require task visibility for user."""
        label = self.label_service.create_label("frontend")
        self.task_repository._tasks[1] = Task(
            id=1,
            title="Task",
            description="Description",
            created_by_user_id=1,
            created_at="now",
        )
        self.task_repository._participants[1] = {2}

        with self.assertRaises(LabelAssignmentError):
            self.label_service.add_label_to_task(1, label.id, 1)

    def test_add_label_to_task_requires_signed_in_user(self):
        """Label assignment should require signed-in user."""
        label = self.label_service.create_label("frontend")

        with self.assertRaises(LabelAssignmentError):
            self.label_service.add_label_to_task(1, label.id, None)

    def test_add_label_to_task_requires_task_id(self):
        """Label assignment should require task id."""
        label = self.label_service.create_label("frontend")

        with self.assertRaises(LabelAssignmentError):
            self.label_service.add_label_to_task(None, label.id, 1)

    def test_add_label_to_task_requires_label_id(self):
        """Label assignment should require label id."""
        self.task_repository._tasks[1] = Task(
            id=1,
            title="Task",
            description="Description",
            created_by_user_id=1,
            created_at="now",
        )
        self.task_repository._participants[1] = {1}

        with self.assertRaises(LabelAssignmentError):
            self.label_service.add_label_to_task(1, None, 1)

    def test_add_label_to_task_requires_existing_label(self):
        """Label assignment should require existing label."""
        self.task_repository._tasks[1] = Task(
            id=1,
            title="Task",
            description="Description",
            created_by_user_id=1,
            created_at="now",
        )
        self.task_repository._participants[1] = {1}

        with self.assertRaises(LabelAssignmentError):
            self.label_service.add_label_to_task(1, 999, 1)


if __name__ == "__main__":
    unittest.main()
