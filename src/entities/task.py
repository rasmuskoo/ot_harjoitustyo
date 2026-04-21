"""Task entity."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a task shown on a user's home page."""

    title: str
    description: str
    created_by_user_id: int
    created_at: str
    project_id: int | None = None
    is_completed: bool = False
    id: int | None = None
