"""CLI home view for authenticated users."""

from src.entities.task import Task
from src.repositories.task_repository import TaskRepository
from src.services.session_service import SessionService
from src.services.task_service import (
    TaskCompleteError,
    TaskCreationError,
    TaskDeleteError,
    TaskEditError,
    TaskService,
)


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

            tasks = self._render_home(user.first_name, user.last_name, user.id)
            command = self._build_command_prompt(tasks)

            if command == "2":
                self._session_service.sign_out()
                print("You have been signed out.")
                return

            if command == "3":
                self._handle_create_task(user.id)
                continue

            if command == "4" and tasks:
                self._handle_edit_task(user.id, tasks)
                continue

            if command == "5" and tasks:
                self._handle_complete_task(user.id, tasks)
                continue

            if command == "6" and tasks:
                self._handle_delete_task(user.id, tasks)
                continue

            if command == "7":
                self._handle_view_completed_tasks(user.id)
                continue

            if command != "1":
                print("Unknown action.")

    def _render_home(self, first_name: str, last_name: str, user_id: int | None) -> list[Task]:
        """Print user home page with task list and return listed tasks."""
        print("\nTaskBoard - Home")
        print(f"Signed in as: {first_name} {last_name}")

        if user_id is None:
            print("No tasks available.")
            return []

        tasks = self._task_repository.list_tasks_for_user(user_id)
        if not tasks:
            print("No tasks found for your account.")
            return []

        print("Your tasks:")
        for index, task in enumerate(tasks, start=1):
            print(f"{index}. {task.title}: {task.description}")
        return tasks

    def _build_command_prompt(self, tasks: list[Task]) -> str:
        """Build command prompt and return selected command."""
        options = "1=refresh, 2=sign out, 3=create task, 7=view completed tasks"
        if tasks:
            options = f"{options}, 4=edit task, 5=complete task, 6=delete task"
        return input(f"Select action ({options}): ").strip()

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

    def _handle_edit_task(self, user_id: int | None, tasks: list[Task]) -> None:
        """Prompt task selection and update header and description."""
        if user_id is None:
            print("Task edit failed: Signed-in user is required.")
            return

        selected_task = self._select_task(tasks, "edit")
        if selected_task is None:
            return

        new_header = input("New header: ")
        new_description = input("New description: ")

        try:
            updated_task = self._task_service.edit_task(
                task_id=selected_task.id,
                user_id=user_id,
                title=new_header,
                description=new_description,
            )
            print(f"Task updated: {updated_task.title}")
        except TaskEditError as error:
            print(f"Task edit failed: {error}")

    def _handle_complete_task(self, user_id: int | None, tasks: list[Task]) -> None:
        """Prompt task selection and complete selected task."""
        if user_id is None:
            print("Task completion failed: Signed-in user is required.")
            return

        selected_task = self._select_task(tasks, "complete")
        if selected_task is None:
            return

        try:
            self._task_service.complete_task(task_id=selected_task.id, user_id=user_id)
            print(f"Task completed: {selected_task.title}")
        except TaskCompleteError as error:
            print(f"Task completion failed: {error}")

    def _handle_delete_task(self, user_id: int | None, tasks: list[Task]) -> None:
        """Prompt task selection and delete selected task."""
        if user_id is None:
            print("Task deletion failed: Signed-in user is required.")
            return

        selected_task = self._select_task(tasks, "delete")
        if selected_task is None:
            return

        try:
            self._task_service.delete_task(task_id=selected_task.id, user_id=user_id)
            print(f"Task deleted: {selected_task.title}")
        except TaskDeleteError as error:
            print(f"Task deletion failed: {error}")

    def _select_task(self, tasks: list[Task], action: str) -> Task | None:
        """Prompt user to select task number for a given action."""
        selection = input(f"Select task number to {action}: ").strip()
        if not selection.isdigit():
            print(f"Task {action} failed: Invalid selection.")
            return None

        task_index = int(selection) - 1
        if task_index < 0 or task_index >= len(tasks):
            print(f"Task {action} failed: Selection out of range.")
            return None

        selected_task = tasks[task_index]
        if selected_task.id is None:
            print(f"Task {action} failed: Selected task has no id.")
            return None

        return selected_task

    def _handle_view_completed_tasks(self, user_id: int | None) -> None:
        """Show completed tasks for signed-in user."""
        if user_id is None:
            print("Completed task view failed: Signed-in user is required.")
            return

        completed_tasks = self._task_repository.list_completed_tasks_for_user(user_id)
        print("\nCompleted Tasks")
        if not completed_tasks:
            print("No completed tasks found for your account.")
            return

        for index, task in enumerate(completed_tasks, start=1):
            print(f"{index}. {task.title}: {task.description}")
