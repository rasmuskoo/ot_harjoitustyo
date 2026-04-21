"""CLI home view for authenticated users."""

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.services.project_service import (
    ProjectCreationError,
    ProjectDetails,
    ProjectService,
    ProjectTaskError,
)
from src.services.session_service import SessionService
from src.services.task_service import (
    TaskCompleteError,
    TaskCreationContext,
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
        user_repository: UserRepository,
        task_repository: TaskRepository,
        project_service: ProjectService,
        task_service: TaskService,
    ) -> None:
        """Create home view dependencies."""
        self._session_service = session_service
        self._user_repository = user_repository
        self._task_repository = task_repository
        self._project_service = project_service
        self._task_service = task_service

    def run(self) -> bool:
        """Run the home view until user signs out or quits the program."""
        while self._session_service.is_authenticated():
            user = self._session_service.get_current_user()
            if user is None:
                break

            tasks = self._render_home(user.first_name, user.last_name, user.id)
            command = self._build_command_prompt(tasks)

            if command == "2":
                self._session_service.sign_out()
                print("You have been signed out.")
                return True

            if command == "q": #Codex generated
                return False

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

            if command == "8":
                self._handle_create_project(user.id)
                continue

            if command == "9":
                self._handle_manage_project(user.id)
                continue

            if command != "1":
                print("Unknown action.")
        return True

    def show(self) -> bool:
        """Display home view."""
        return self.run()

    def _render_home(self, first_name: str, last_name: str, user_id: int | None) -> list[Task]:
        """Print user home page with task list and return listed tasks."""
        print("\nTaskBoard - Home")
        print(f"Signed in as: {first_name} {last_name}")

        if user_id is None:
            print("No tasks available.")
            return []

        tasks = self._task_repository.list_tasks_for_user(user_id)
        projects = self._project_service.list_projects_for_user(user_id)
        if not tasks:
            print("No tasks found for your account.")
        else:
            print("Your tasks:")
            for index, task in enumerate(tasks, start=1):
                print(f"{index}. {task.title}: {task.description}")

        if projects:
            print("Your projects:")
            for index, project in enumerate(projects, start=1):
                print(f"{index}. {project.name}")
        else:
            print("No projects found for your account.")
        return tasks

    def _build_command_prompt(self, tasks: list[Task]) -> str:
        """Build command prompt and return selected command."""
        options = (
            "1=refresh, 2=sign out, 3=create task, 7=view completed tasks, "
            "8=create project, 9=view projects, q=quit"
        )
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
                context=TaskCreationContext(creator_user_id=user_id),
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

    def _handle_create_project(self, user_id: int | None) -> None:
        """Prompt for project fields and create a project."""
        print("\nCreate Project")
        name = input("Project name: ")
        users = self._user_repository.list_users()
        if not users:
            print("Project creation failed: No users available.")
            return

        selected_user_ids = self._select_users(users)
        try:
            project = self._project_service.create_project(name, user_id, selected_user_ids)
            print(f"Project created: {project.name}")
        except ProjectCreationError as error:
            print(f"Project creation failed: {error}")

    def _handle_manage_project(self, user_id: int | None) -> None:
        """Display projects and allow project-specific task actions."""
        projects = self._project_service.list_projects_for_user(user_id)
        if not projects:
            print("No projects found for your account.")
            return

        project = self._select_project(projects)
        if project is None:
            return

        try:
            details = self._project_service.get_project_details(project.id, user_id)
        except ProjectTaskError as error:
            print(f"Project view failed: {error}")
            return

        self._render_project(details)
        action = input("Select action (1=back, 2=create task, 3=add existing task): ").strip()
        if action == "2":
            self._handle_create_task_for_project(details, user_id)
        elif action == "3":
            self._handle_add_existing_task_to_project(details, user_id)

    def _render_project(self, details: ProjectDetails) -> None:
        """Print project details, members, and tasks."""
        print(f"\nProject: {details.project.name}")
        print("Members:")
        for index, member in enumerate(details.members, start=1):
            print(f"{index}. {member.first_name} {member.last_name} ({member.email})")

        print("Tasks:")
        if not details.tasks:
            print("No tasks in this project.")
            return

        for index, task in enumerate(details.tasks, start=1):
            print(f"{index}. {task.title}: {task.description}")

    def _handle_create_task_for_project(self, details: ProjectDetails, user_id: int | None) -> None:
        """Prompt for fields and create a new task inside a project."""
        print("\nCreate Project Task")
        header = input("Header: ")
        description = input("Description: ")
        member_ids = [member.id for member in details.members if member.id is not None]

        try:
            task = self._task_service.create_task(
                title=header,
                description=description,
                context=TaskCreationContext(
                    creator_user_id=user_id,
                    project_id=details.project.id,
                    participant_user_ids=member_ids,
                ),
            )
            print(f"Task created in project: {task.title}")
        except TaskCreationError as error:
            print(f"Project task creation failed: {error}")

    def _handle_add_existing_task_to_project(
        self,
        details: ProjectDetails,
        user_id: int | None,
    ) -> None:
        """Prompt task selection and link an existing task to the project."""
        available_tasks = self._project_service.list_available_tasks_for_project(
            details.project.id,
            user_id,
        )
        if not available_tasks:
            print("No existing tasks available to add.")
            return

        selected_task = self._select_task(available_tasks, "add to project")
        if selected_task is None:
            return

        try:
            self._project_service.add_existing_task_to_project(
                details.project.id,
                selected_task.id,
                user_id,
            )
            print(f"Task added to project: {selected_task.title}")
        except ProjectTaskError as error:
            print(f"Project task update failed: {error}")

    def _select_users(self, users: list[User]) -> list[int]:
        """Prompt user selection by comma-separated list."""
        print("Select project members by number, separated by commas:")
        for index, user in enumerate(users, start=1):
            print(f"{index}. {user.first_name} {user.last_name} ({user.email})")

        selection = input("Members: ").strip()
        if not selection:
            return []

        selected_user_ids: list[int] = []
        for token in selection.split(","):
            candidate = token.strip()
            if not candidate.isdigit():
                continue
            user_index = int(candidate) - 1
            if 0 <= user_index < len(users) and users[user_index].id is not None:
                selected_user_ids.append(users[user_index].id)
        return selected_user_ids

    def _select_project(self, projects: list[Project]) -> Project | None:
        """Prompt user to select one project by number."""
        print("\nProjects")
        for index, project in enumerate(projects, start=1):
            print(f"{index}. {project.name}")

        selection = input("Select project number: ").strip()
        if not selection.isdigit():
            print("Project selection failed: Invalid selection.")
            return None

        project_index = int(selection) - 1
        if project_index < 0 or project_index >= len(projects):
            print("Project selection failed: Selection out of range.")
            return None
        return projects[project_index]
