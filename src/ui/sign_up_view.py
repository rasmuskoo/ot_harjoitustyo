"""CLI sign-up view for user registration."""

from getpass import getpass

from src.services.auth_service import AuthService, RegistrationError


class SignUpView:
    """Handles user input/output for account registration."""

    def __init__(self, auth_service: AuthService) -> None:
        """Create the view with registration service dependency."""
        self._auth_service = auth_service

    def run(self) -> None:
        """Run one sign-up flow in the terminal."""
        print("TaskBoard - Create Account")

        first_name = self._prompt("First name: ")
        last_name = self._prompt("Last name: ")
        email = self._prompt("Email: ")
        password = self._prompt_secret("Password: ")
        confirm_password = self._prompt_secret("Confirm password: ")

        try:
            user = self._auth_service.register(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                confirm_password=confirm_password,
            )
            print(f"Account created for {user.first_name} {user.last_name} ({user.email}).")
        except RegistrationError as error:
            print(f"Registration failed: {error}")

    def _prompt(self, label: str) -> str:
        """Show a flushed prompt and read one input line."""
        print(label, end="", flush=True)
        return input()

    def _prompt_secret(self, label: str) -> str:
        """Read hidden input when possible, fallback to visible input."""
        try:
            return getpass(label)
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception:
            return self._prompt(label)
