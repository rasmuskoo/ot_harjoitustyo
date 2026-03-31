"""Application entry point for TaskBoard desktop."""

from src.repositories.database import initialize_database
from src.services.auth_service import AuthService
from src.ui.sign_up_view import SignUpView


def main() -> None:
    """Start the application and launch registration view."""
    initialize_database()
    auth_service = AuthService()
    sign_up_view = SignUpView(auth_service)
    sign_up_view.run()


if __name__ == "__main__":
    main()
