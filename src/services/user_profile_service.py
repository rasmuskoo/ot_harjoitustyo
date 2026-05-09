"""User profile application service logic."""

from dataclasses import dataclass

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository


class UserProfileError(Exception):
    """Raised when user profile data cannot be loaded."""


@dataclass
class UserProfile:
    """Data shown on a user's profile page.

    Attributes:
        user: User whose page is shown.
        projects: Projects where the user is a member.
        tasks: Tasks where the user is a participant.
    """

    user: User
    projects: list[Project]
    tasks: list[Task]


class UserProfileService:
    """Collects user profile data from repositories."""

    def __init__(
        self,
        user_repository: UserRepository | None = None,
        project_repository: ProjectRepository | None = None,
        task_repository: TaskRepository | None = None,
    ) -> None:
        """Create a user profile service."""
        self._user_repository = user_repository or UserRepository()
        self._project_repository = project_repository or ProjectRepository()
        self._task_repository = task_repository or TaskRepository()

    def get_profile(self, user_id: int | None) -> UserProfile:
        """Return profile data for a user.

        Args:
            user_id: Id of the user whose profile is shown.

        Returns:
            User profile including project and task participation.

        Raises:
            UserProfileError: If user id is missing or user does not exist.
        """
        if user_id is None:
            raise UserProfileError("User id is required.")

        user = self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserProfileError("User was not found.")

        projects = self._project_repository.list_projects_for_user(user_id)
        tasks = self._task_repository.list_all_tasks_for_user(user_id)
        return UserProfile(user=user, projects=projects, tasks=tasks)
