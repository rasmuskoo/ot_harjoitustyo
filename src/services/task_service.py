"""Task-related application service logic."""

from datetime import datetime, timezone

from src.entities.task import Task
from src.repositories.task_repository import TaskRepository


class TaskCreationError(Exception):
    """Raised when task creation validation fails."""


class TaskService:
    """Handles task creation and participant linking."""

    def __init__(self, task_repository: TaskRepository | None = None) -> None:
        """Create task service with optional repository dependency."""
        self._task_repository = task_repository or TaskRepository()

    def create_task(self, title: str, description: str, creator_user_id: int | None) -> Task:
        """Create a task and link creator as a participant."""
        normalized_title = title.strip()
        normalized_description = description.strip()

        if not normalized_title:
            raise TaskCreationError("Task header is required.")
        if not normalized_description:
            raise TaskCreationError("Task description is required.")
        if creator_user_id is None:
            raise TaskCreationError("Signed-in user is required to create a task.")

        task = Task(
            title=normalized_title,
            description=normalized_description,
            created_by_user_id=creator_user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        created_task = self._task_repository.create_task(task)
        if created_task.id is None:
            raise TaskCreationError("Task creation failed.")

        self._task_repository.add_participant(created_task.id, creator_user_id)
        return created_task
