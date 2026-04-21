"""Task-related application service logic."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.entities.task import Task
from src.repositories.task_repository import TaskRepository


class TaskCreationError(Exception):
    """Raised when task creation validation fails."""


class TaskEditError(Exception):
    """Raised when task editing validation fails."""


class TaskCompleteError(Exception):
    """Raised when task completion fails."""


class TaskDeleteError(Exception):
    """Raised when task deletion fails."""


@dataclass
class TaskCreationContext:
    """Extra metadata for task creation."""

    creator_user_id: int | None
    project_id: int | None = None
    participant_user_ids: list[int] | None = None


class TaskService:
    """Handles task creation, update, completion, and deletion."""

    def __init__(self, task_repository: TaskRepository | None = None) -> None:
        """Create task service with optional repository dependency."""
        self._task_repository = task_repository or TaskRepository()

    def create_task(
        self,
        title: str,
        description: str,
        context: TaskCreationContext,
    ) -> Task:
        """Create a task and link creator as a participant."""
        normalized_title = title.strip()
        normalized_description = description.strip()

        if not normalized_title:
            raise TaskCreationError("Task header is required.")
        if not normalized_description:
            raise TaskCreationError("Task description is required.")
        if context.creator_user_id is None:
            raise TaskCreationError("Signed-in user is required to create a task.")

        task = Task(
            title=normalized_title,
            description=normalized_description,
            created_by_user_id=context.creator_user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            project_id=context.project_id,
        )
        created_task = self._task_repository.create_task(task)
        if created_task.id is None:
            raise TaskCreationError("Task creation failed.")

        participant_ids = list(
            dict.fromkeys(context.participant_user_ids or [context.creator_user_id])
        )
        if context.creator_user_id not in participant_ids:
            participant_ids.insert(0, context.creator_user_id)

        self._task_repository.add_participants(created_task.id, participant_ids)
        return created_task

    def edit_task(
        self,
        task_id: int,
        user_id: int | None,
        title: str,
        description: str,
    ) -> Task:
        """Edit task header and description for a participant user."""
        normalized_title = title.strip()
        normalized_description = description.strip()

        if user_id is None:
            raise TaskEditError("Signed-in user is required to edit a task.")
        if not normalized_title:
            raise TaskEditError("Task header is required.")
        if not normalized_description:
            raise TaskEditError("Task description is required.")

        existing_task = self._task_repository.find_task_for_user(task_id, user_id)
        if existing_task is None:
            raise TaskEditError("Task was not found for this user.")

        was_updated = self._task_repository.update_task_for_user(
            task_id=task_id,
            user_id=user_id,
            title=normalized_title,
            description=normalized_description,
        )
        if not was_updated:
            raise TaskEditError("Task update failed.")

        updated_task = self._task_repository.find_task_for_user(task_id, user_id)
        if updated_task is None:
            raise TaskEditError("Task was not found after update.")
        return updated_task

    def complete_task(self, task_id: int, user_id: int | None) -> None:
        """Mark task as completed for a participant user."""
        if user_id is None:
            raise TaskCompleteError("Signed-in user is required to complete a task.")

        task = self._task_repository.find_task_for_user(task_id, user_id)
        if task is None:
            raise TaskCompleteError("Task was not found for this user.")
        if task.is_completed:
            raise TaskCompleteError("Task is already completed.")

        was_completed = self._task_repository.complete_task_for_user(task_id, user_id)
        if not was_completed:
            raise TaskCompleteError("Task completion failed.")

    def delete_task(self, task_id: int, user_id: int | None) -> None:
        """Delete task for a participant user."""
        if user_id is None:
            raise TaskDeleteError("Signed-in user is required to delete a task.")

        task = self._task_repository.find_task_for_user(task_id, user_id)
        if task is None:
            raise TaskDeleteError("Task was not found for this user.")

        was_deleted = self._task_repository.delete_task_for_user(task_id, user_id)
        if not was_deleted:
            raise TaskDeleteError("Task deletion failed.")
