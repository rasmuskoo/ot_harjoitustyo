"""Application entry point for TaskBoard desktop."""

from src.repositories.database import initialize_database
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.project_service import ProjectService
from src.services.session_service import SessionService
from src.services.task_service import TaskService
from src.ui.home_view import HomeView
from src.ui.sign_in_view import SignInView
from src.ui.sign_up_view import SignUpView


def _build_views() -> tuple[SignInView, HomeView]:
    """Construct application repositories, services, and views."""
    auth_service = AuthService()
    session_service = SessionService()
    user_repository = UserRepository()
    task_repository = TaskRepository()
    project_repository = ProjectRepository()
    task_service = TaskService(task_repository)
    project_service = ProjectService(project_repository, task_repository)

    sign_up_view = SignUpView(auth_service)
    sign_in_view = SignInView(auth_service, session_service, sign_up_view)
    home_view = HomeView(
        session_service,
        user_repository,
        task_repository,
        project_service,
        task_service,
    )
    return sign_in_view, home_view


def main() -> None:
    """Start the application and run signed-in/signed-out flow."""
    try:
        initialize_database()
        sign_in_view, home_view = _build_views()

        while True:
            continue_running = sign_in_view.run()
            if not continue_running:
                print("Exiting TaskBoard.") #Codex generated quit feature
                return

            continue_running = home_view.run()
            if not continue_running:
                print("Exiting TaskBoard.") #Codex generated quit feature
                return
    except KeyboardInterrupt:
        print("\nExiting TaskBoard.")


if __name__ == "__main__":
    main()
