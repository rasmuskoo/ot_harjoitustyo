"""Project-related application service logic."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository


class ProjectCreationError(Exception):
    """Raised when project creation validation fails."""


class ProjectTaskError(Exception):
    """Raised when project task operations fail."""


class ProjectDeleteError(Exception):
    """Raised when project deletion fails."""


@dataclass
class ProjectDetails:
    """Project aggregate for project view rendering."""

    project: Project
    members: list[User]
    tasks: list[Task]


class ProjectService:
    """Handles project creation and task assignment in projects."""

    def __init__(
        self,
        project_repository: ProjectRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        """Create project service with optional repository dependencies."""
        self._project_repository = project_repository or ProjectRepository()
        self._task_repository = task_repository or TaskRepository()

    def create_project(
        self,
        name: str,
        owner_user_id: int | None,
        member_user_ids: list[int],
    ) -> Project:
        """Create a project and attach selected members."""
        normalized_name = name.strip()
        if owner_user_id is None:
            raise ProjectCreationError("Signed-in user is required to create a project.")
        if not normalized_name:
            raise ProjectCreationError("Project name is required.")

        unique_member_ids = list(dict.fromkeys(member_user_ids))
        if owner_user_id not in unique_member_ids:
            unique_member_ids.insert(0, owner_user_id)

        project = Project(
            name=normalized_name,
            created_by_user_id=owner_user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        created_project = self._project_repository.create_project(project)
        if created_project.id is None:
            raise ProjectCreationError("Project creation failed.")

        for member_id in unique_member_ids:
            self._project_repository.add_member(created_project.id, member_id)
        return created_project

    def list_projects_for_user(self, user_id: int | None) -> list[Project]:
        """Return projects for current user."""
        if user_id is None:
            return []
        return self._project_repository.list_projects_for_user(user_id)

    def get_project_details(self, project_id: int, user_id: int | None) -> ProjectDetails:
        """Return project, members, and tasks for a member user."""
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
        """Link an existing user-visible task to a project and share it with project members."""
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
        """Delete a project for its creator and unlink its tasks."""
        if user_id is None:
            raise ProjectDeleteError("Signed-in user is required to delete a project.")

        project = self._project_repository.find_project_for_user(project_id, user_id)
        if project is None:
            raise ProjectDeleteError("Project was not found for this user.")

        was_deleted = self._project_repository.delete_project_for_user(project_id, user_id)
        if not was_deleted:
            raise ProjectDeleteError("Only the project creator can delete the project.")
