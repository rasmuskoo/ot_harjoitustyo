"""Project entity."""

from dataclasses import dataclass


@dataclass
class Project:
    """Represents a project that groups users and tasks.

    Attributes:
        name: Project name shown in project lists.
        created_by_user_id: Id of the user who created the project.
        created_at: Creation time stored as an ISO formatted string.
        priority: Project priority. Allowed values are low, medium, and high.
        due_date: Optional project due date in YYYY-MM-DD format.
        id: Database id for the project, or None before the project is stored.
    """

    name: str
    created_by_user_id: int
    created_at: str
    priority: str = "medium"
    due_date: str | None = None
    id: int | None = None
