"""CLI home view for authenticated users."""

from src.repositories.task_repository import TaskRepository
from src.services.session_service import SessionService
from src.services.task_service import TaskCreationError, TaskService


class HomeView:
    """Displays signed-in user home page and allows sign out."""

    def __init__(
        self,
        session_service: SessionService,
        task_repository: TaskRepository,
        task_service: TaskService,
    ) -> None:
        """Create home view dependencies."""
        self._session_service = session_service
        self._task_repository = task_repository
        self._task_service = task_service

    def run(self) -> None:
        """Run the home view until user signs out."""
        while self._session_service.is_authenticated():
            user = self._session_service.get_current_user()
            if user is None:
                break

            self._render_home(user.first_name, user.last_name, user.id)
            command = input("Select action (1=refresh, 2=sign out, 3=create task): ").strip()

            if command == "2":
                self._session_service.sign_out()
                print("You have been signed out.")
                return

            if command == "3":
                self._handle_create_task(user.id)
                continue

            if command != "1":
                print("Unknown action.")

    def _render_home(self, first_name: str, last_name: str, user_id: int | None) -> None:
        """Print user home page with task list."""
        print("\nTaskBoard - Home")
        print(f"Signed in as: {first_name} {last_name}")

        if user_id is None:
            print("No tasks available.")
            return

        tasks = self._task_repository.list_tasks_for_user(user_id)
        if not tasks:
            print("No tasks found for your account.")
            return

        print("Your tasks:")
        for task in tasks:
            print(f"- {task.title}: {task.description}")

    def _handle_create_task(self, user_id: int | None) -> None:
        """Prompt for task fields and create a task for the current user."""
        print("\nCreate Task")
        header = input("Header: ")
        description = input("Description: ")

        try:
            task = self._task_service.create_task(
                title=header,
                description=description,
                creator_user_id=user_id,
            )
            print(f"Task created: {task.title}")
        except TaskCreationError as error:
            print(f"Task creation failed: {error}")
