"""Application entry point for TaskBoard desktop."""

from src.repositories.database import initialize_database
from src.repositories.task_repository import TaskRepository
from src.services.auth_service import AuthService
from src.services.session_service import SessionService
from src.ui.home_view import HomeView
from src.ui.sign_in_view import SignInView
from src.ui.sign_up_view import SignUpView


def main() -> None:
    """Start the application and run signed-in/signed-out flow."""
    initialize_database()

    auth_service = AuthService()
    session_service = SessionService()
    task_repository = TaskRepository()

    sign_up_view = SignUpView(auth_service)
    sign_in_view = SignInView(auth_service, session_service, sign_up_view)
    home_view = HomeView(session_service, task_repository)

    while True:
        sign_in_view.run()
        home_view.run()


if __name__ == "__main__":
    main()
