"""Project-related application service logic."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository

VALID_PRIORITIES = {"low", "medium", "high"}
DEFAULT_PRIORITY = "medium"


class ProjectCreationError(Exception):
    """Raised when project creation validation fails."""


class ProjectTaskError(Exception):
    """Raised when project task operations fail."""


class ProjectDeleteError(Exception):
    """Raised when project deletion fails."""


@dataclass
class ProjectDetails:
    """Project data shown in the project view.

    Attributes:
        project: Project being displayed.
        members: Users who belong to the project.
        tasks: Tasks linked to the project.
    """

    project: Project
    members: list[User]
    tasks: list[Task]


@dataclass
class ProjectCreationContext:
    """Extra metadata for project creation.

    Attributes:
        owner_user_id: Id of the user creating the project.
        member_user_ids: Users selected as project members.
        priority: Requested project priority.
        due_date: Optional due date in YYYY-MM-DD format.
    """

    owner_user_id: int | None
    member_user_ids: list[int]
    priority: str = DEFAULT_PRIORITY
    due_date: str = ""


class ProjectService:
    """Handles project validation, membership, and task assignment rules."""

    def __init__(
        self,
        project_repository: ProjectRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        """Create a project service.

        Args:
            project_repository: Repository used for project persistence.
            task_repository: Repository used when assigning tasks to projects.
        """
        self._project_repository = project_repository or ProjectRepository()
        self._task_repository = task_repository or TaskRepository()

    def create_project(
        self,
        name: str,
        context: ProjectCreationContext,
    ) -> Project:
        """Create a project and attach selected members.

        Args:
            name: Project name entered by the user.
            context: Project owner, selected members, priority, and due date.

        Returns:
            The stored project with its database id.

        Raises:
            ProjectCreationError: If required input is missing or invalid.
        """
        normalized_name = name.strip()
        if context.owner_user_id is None:
            raise ProjectCreationError("Signed-in user is required to create a project.")
        if not normalized_name:
            raise ProjectCreationError("Project name is required.")

        normalized_priority = self._normalize_priority(context.priority)
        normalized_due_date = self._normalize_due_date(context.due_date)
        unique_member_ids = list(dict.fromkeys(context.member_user_ids))
        if context.owner_user_id not in unique_member_ids:
            unique_member_ids.insert(0, context.owner_user_id)

        project = Project(
            name=normalized_name,
            created_by_user_id=context.owner_user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            priority=normalized_priority,
            due_date=normalized_due_date,
        )
        created_project = self._project_repository.create_project(project)
        if created_project.id is None:
            raise ProjectCreationError("Project creation failed.")

        for member_id in unique_member_ids:
            self._project_repository.add_member(created_project.id, member_id)
        return created_project

    def list_projects_for_user(self, user_id: int | None) -> list[Project]:
        """Return projects visible to the current user.

        Args:
            user_id: Id of the current user.

        Returns:
            Projects where the user is a member.
        """
        if user_id is None:
            return []
        return self._project_repository.list_projects_for_user(user_id)

    def get_project_details(self, project_id: int, user_id: int | None) -> ProjectDetails:
        """Return project, members, and tasks for a project member.

        Args:
            project_id: Id of the project to display.
            user_id: Id of the current user.

        Returns:
            Project details for the project view.

        Raises:
            ProjectTaskError: If the user cannot access the project.
        """
        if user_id is None:
            raise ProjectTaskError("Signed-in user is required.")

        project = self._project_repository.find_project_for_user(project_id, user_id)
        if project is None:
            raise ProjectTaskError("Project was not found for this user.")

        members = self._project_repository.list_members(project_id)
        tasks = self._project_repository.list_tasks(project_id)
        return ProjectDetails(project=project, members=members, tasks=tasks)

    def add_existing_task_to_project(
        self,
        project_id: int,
        task_id: int,
        user_id: int | None,
    ) -> None:
        """Link an existing user-visible task to a project.

        Args:
            project_id: Id of the target project.
            task_id: Id of the task being added.
            user_id: Id of the current user.

        Raises:
            ProjectTaskError: If the project or task cannot be accessed.
        """
        details = self.get_project_details(project_id, user_id)
        if not self._task_repository.assign_task_to_project_for_user(task_id, project_id, user_id):
            raise ProjectTaskError("Task could not be added to the project.")

        member_ids = [member.id for member in details.members if member.id is not None]
        self._task_repository.add_participants(task_id, member_ids)

    def list_available_tasks_for_project(self, project_id: int, user_id: int | None) -> list[Task]:
        """Return user-visible tasks that are not yet part of a project."""
        self.get_project_details(project_id, user_id)
        if user_id is None:
            return []
        return self._task_repository.list_unassigned_tasks_for_user(user_id)

    def delete_project(self, project_id: int, user_id: int | None) -> None:
        """Delete a project for its creator and unlink its tasks.

        Args:
            project_id: Id of the project to delete.
            user_id: Id of the current user.

        Raises:
            ProjectDeleteError: If the project is missing or the user is not
                allowed to delete it.
        """
        if user_id is None:
            raise ProjectDeleteError("Signed-in user is required to delete a project.")

        project = self._project_repository.find_project_for_user(project_id, user_id)
        if project is None:
            raise ProjectDeleteError("Project was not found for this user.")

        was_deleted = self._project_repository.delete_project_for_user(project_id, user_id)
        if not was_deleted:
            raise ProjectDeleteError("Only the project creator can delete the project.")

    def _normalize_priority(self, priority: str) -> str:
        """Return normalized priority or raise validation error."""
        normalized_priority = priority.strip().lower() or DEFAULT_PRIORITY
        if normalized_priority not in VALID_PRIORITIES:
            allowed_priorities = ", ".join(sorted(VALID_PRIORITIES))
            raise ProjectCreationError(f"Priority must be one of: {allowed_priorities}.")
        return normalized_priority

    def _normalize_due_date(self, due_date: str) -> str | None:
        """Return normalized due date or raise validation error."""
        normalized_due_date = due_date.strip()
        if not normalized_due_date:
            return None

        try:
            datetime.strptime(normalized_due_date, "%Y-%m-%d")
        except ValueError as error:
            raise ProjectCreationError("Due date must use YYYY-MM-DD format.") from error
        return normalized_due_date
