"""CLI sign-up view for user registration."""

from src.services.auth_service import AuthService, RegistrationError, RegistrationInput
from src.ui.prompt_utils import prompt, prompt_secret


class SignUpView:
    """Handles user input/output for account registration."""

    def __init__(self, auth_service: AuthService) -> None:
        """Create the view with registration service dependency."""
        self._auth_service = auth_service

    def run(self) -> None:
        """Run one sign-up flow in the terminal."""
        print("TaskBoard - Create Account")

        first_name = prompt("First name: ")
        last_name = prompt("Last name: ")
        email = prompt("Email: ")
        password = prompt_secret("Password: ")
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
        except RegistrationError as error:
            print(f"Registration failed: {error}")

    def show(self) -> None:
        """Display sign-up view."""
        self.run()
