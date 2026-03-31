"""Task entity."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a task shown on a user's home page."""

    title: str
    description: str
    created_by_user_id: int
    created_at: str
    id: int | None = None
