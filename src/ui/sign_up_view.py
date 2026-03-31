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

        first_name = input("First name: ")
        last_name = input("Last name: ")
        email = input("Email: ")
        password = getpass("Password: ")
        confirm_password = getpass("Confirm password: ")

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
