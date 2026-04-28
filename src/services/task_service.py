"""Task-related application service logic."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.entities.task import Task
from src.repositories.task_repository import TaskRepository

VALID_PRIORITIES = {"low", "medium", "high"}
DEFAULT_PRIORITY = "medium"


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
    """Extra metadata for task creation.

    Attributes:
        creator_user_id: Id of the user creating the task.
        project_id: Optional project id when the task is created inside a project.
        participant_user_ids: Users who should see the created task.
        priority: Requested task priority.
        due_date: Optional due date in YYYY-MM-DD format.
    """

    creator_user_id: int | None
    project_id: int | None = None
    participant_user_ids: list[int] | None = None
    priority: str = DEFAULT_PRIORITY
    due_date: str = ""


class TaskService:
    """Handles task validation and task-related application rules."""

    def __init__(self, task_repository: TaskRepository | None = None) -> None:
        """Create a task service.

        Args:
            task_repository: Repository used for task persistence. A default
                repository is created when this is None.
        """
        self._task_repository = task_repository or TaskRepository()

    def create_task(
        self,
        title: str,
        description: str,
        context: TaskCreationContext,
    ) -> Task:
        """Create a task and link it to its participants.

        Args:
            title: Task title entered by the user.
            description: Task description entered by the user.
            context: Metadata such as creator, project, priority, and due date.

        Returns:
            The stored task with its database id.

        Raises:
            TaskCreationError: If required input is missing or invalid.
        """
        normalized_title = title.strip()
        normalized_description = description.strip()

        if not normalized_title:
            raise TaskCreationError("Task header is required.")
        if not normalized_description:
            raise TaskCreationError("Task description is required.")
        if context.creator_user_id is None:
            raise TaskCreationError("Signed-in user is required to create a task.")

        priority = self._normalize_priority(context.priority)
        due_date = self._normalize_due_date(context.due_date)
        task = Task(
            title=normalized_title,
            description=normalized_description,
            created_by_user_id=context.creator_user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            priority=priority,
            due_date=due_date,
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

    def _normalize_priority(self, priority: str) -> str:
        """Return normalized priority or raise validation error."""
        normalized_priority = priority.strip().lower() or DEFAULT_PRIORITY
        if normalized_priority not in VALID_PRIORITIES:
            allowed_priorities = ", ".join(sorted(VALID_PRIORITIES))
            raise TaskCreationError(f"Priority must be one of: {allowed_priorities}.")
        return normalized_priority

    def _normalize_due_date(self, due_date: str) -> str | None:
        """Return normalized due date or raise validation error."""
        normalized_due_date = due_date.strip()
        if not normalized_due_date:
            return None

        try:
            datetime.strptime(normalized_due_date, "%Y-%m-%d")
        except ValueError as error:
            raise TaskCreationError("Due date must use YYYY-MM-DD format.") from error
        return normalized_due_date

    def edit_task(
        self,
        task_id: int,
        user_id: int | None,
        title: str,
        description: str,
    ) -> Task:
        """Edit a task's title and description for a participant user.

        Args:
            task_id: Id of the task being edited.
            user_id: Id of the current user.
            title: New task title.
            description: New task description.

        Returns:
            The updated task.

        Raises:
            TaskEditError: If the task is missing, input is invalid, or the
                user cannot edit the task.
        """
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
        """Mark a task as completed for a participant user.

        Args:
            task_id: Id of the task to complete.
            user_id: Id of the current user.

        Raises:
            TaskCompleteError: If the task is missing, already completed, or
                the user cannot access it.
        """
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
        """Delete a task for a participant user.

        Args:
            task_id: Id of the task to delete.
            user_id: Id of the current user.

        Raises:
            TaskDeleteError: If the task is missing or the user cannot access it.
        """
        if user_id is None:
            raise TaskDeleteError("Signed-in user is required to delete a task.")

        task = self._task_repository.find_task_for_user(task_id, user_id)
        if task is None:
            raise TaskDeleteError("Task was not found for this user.")

        was_deleted = self._task_repository.delete_task_for_user(task_id, user_id)
        if not was_deleted:
            raise TaskDeleteError("Task deletion failed.")
