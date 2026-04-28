"""Project entity."""

from dataclasses import dataclass


@dataclass
class Project:
    """Represents a project that groups users and tasks."""

    name: str
    created_by_user_id: int
    created_at: str
    priority: str = "medium"
    id: int | None = None
