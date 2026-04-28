"""Label-related application service logic."""

from src.entities.label import Label
from src.repositories.label_repository import LabelRepository
from src.repositories.task_repository import TaskRepository


class LabelCreationError(Exception):
    """Raised when label creation validation fails."""


class LabelAssignmentError(Exception):
    """Raised when assigning a label to a task fails."""


class LabelService:
    """Handles label validation, searching, and task assignment rules."""

    def __init__(
        self,
        label_repository: LabelRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        """Create a label service.

        Args:
            label_repository: Repository used for label persistence.
            task_repository: Repository used to check task visibility.
        """
        self._label_repository = label_repository or LabelRepository()
        self._task_repository = task_repository or TaskRepository()

    def create_label(self, name: str) -> Label:
        """Create a reusable label with a unique normalized name.

        Args:
            name: Label name entered by the user.

        Returns:
            The stored label with its database id.

        Raises:
            LabelCreationError: If the name is empty or already in use.
        """
        normalized_name = self._normalize_name(name)
        existing_label = self._label_repository.find_by_name(normalized_name)
        if existing_label is not None:
            raise LabelCreationError("Label already exists.")

        created_label = self._label_repository.create_label(Label(name=normalized_name))
        if created_label.id is None:
            raise LabelCreationError("Label creation failed.")
        return created_label

    def list_labels(self) -> list[Label]:
        """Return all labels.

        Returns:
            Labels ordered by the repository.
        """
        return self._label_repository.list_labels()

    def search_labels(self, query: str) -> list[Label]:
        """Return labels matching a search query.

        Args:
            query: Search text entered by the user.

        Returns:
            Matching labels, or all labels when the query is empty.
        """
        normalized_query = query.strip().lower()
        if not normalized_query:
            return self.list_labels()
        return self._label_repository.search_labels(normalized_query)

    def list_labels_for_task(self, task_id: int | None) -> list[Label]:
        """Return labels attached to a task.

        Args:
            task_id: Id of the task whose labels are listed.

        Returns:
            Labels attached to the task, or an empty list without a task id.
        """
        if task_id is None:
            return []
        return self._label_repository.list_labels_for_task(task_id)

    def add_label_to_task(
        self,
        task_id: int | None,
        label_id: int | None,
        user_id: int | None,
    ) -> None:
        """Attach an existing label to a task visible to the current user.

        Args:
            task_id: Id of the task receiving the label.
            label_id: Id of the label being attached.
            user_id: Id of the current user.

        Raises:
            LabelAssignmentError: If the user, task, or label is missing.
        """
        if user_id is None:
            raise LabelAssignmentError("Signed-in user is required.")
        if task_id is None:
            raise LabelAssignmentError("Task id is required.")
        if label_id is None:
            raise LabelAssignmentError("Label id is required.")

        task = self._task_repository.find_task_for_user(task_id, user_id)
        if task is None:
            raise LabelAssignmentError("Task was not found for this user.")

        label = self._label_repository.find_by_id(label_id)
        if label is None:
            raise LabelAssignmentError("Label was not found.")

        self._label_repository.add_label_to_task(task_id, label_id)

    def _normalize_name(self, name: str) -> str:
        """Return normalized label name or raise validation error."""
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise LabelCreationError("Label name is required.")
        return normalized_name
