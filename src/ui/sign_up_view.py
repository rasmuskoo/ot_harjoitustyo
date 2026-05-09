"""CLI sign-up view for user registration."""

from src.services.auth_service import AuthService, RegistrationError, RegistrationInput
from src.ui.prompt_utils import prompt, prompt_secret


class SignUpView:
    """Handles user input/output for account registration."""

    def __init__(self, auth_service: AuthService) -> None:
        """Create the view with registration service dependency."""
        self._auth_service = auth_service

    def run(self) -> None:
        """Run sign-up flow until registration succeeds or user cancels."""
        while True:
            print("TaskBoard - Create Account")
            print("Email must be in format name@example.com.")
            print("Password must be at least 8 characters long.")
            print("Type 'q' as first name to return to sign in.")

            first_name = prompt("First name: ")
            if first_name.strip().lower() == "q":
                return

            last_name = prompt("Last name: ")
            email = prompt("Email (name@example.com): ")
            password = prompt_secret("Password (at least 8 characters): ")
            confirm_password = prompt_secret("Confirm password: ")

            try:
                user = self._auth_service.register(
                    RegistrationInput(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                        confirm_password=confirm_password,
                    )
                )
                print(f"Account created for {user.first_name} {user.last_name} ({user.email}).")
                return
            except RegistrationError as error:
                print(f"Registration failed: {error}")
                print("Please check the fields and try again.\n")

    def show(self) -> None:
        """Display sign-up view."""
        self.run()
