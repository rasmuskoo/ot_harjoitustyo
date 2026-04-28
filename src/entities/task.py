"""Task entity."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a task shown on a user's home page.

    Attributes:
        title: Short task title.
        description: Longer task description.
        created_by_user_id: Id of the user who created the task.
        created_at: Creation time stored as an ISO formatted string.
        priority: Task priority. Allowed values are low, medium, and high.
        due_date: Optional task due date in YYYY-MM-DD format.
        project_id: Id of the linked project, or None for a standalone task.
        is_completed: Whether the task has been marked completed.
        id: Database id for the task, or None before the task is stored.
    """

    title: str
    description: str
    created_by_user_id: int
    created_at: str
    priority: str = "medium"
    due_date: str | None = None
    project_id: int | None = None
    is_completed: bool = False
    id: int | None = None
