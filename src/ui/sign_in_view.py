"""CLI sign-in view for signed-out application state."""

from src.services.auth_service import AuthService, AuthenticationError
from src.services.session_service import SessionService
from src.ui.prompt_utils import prompt, prompt_secret
from src.ui.sign_up_view import SignUpView


class SignInView:
    """Handles sign-in flow and registration redirect for signed-out users."""

    def __init__(
        self,
        auth_service: AuthService,
        session_service: SessionService,
        sign_up_view: SignUpView,
    ) -> None:
        """Create sign-in view dependencies."""
        self._auth_service = auth_service
        self._session_service = session_service
        self._sign_up_view = sign_up_view

    def run(self) -> bool:
        """Run sign-in loop until user is authenticated or user quits."""
        while not self._session_service.is_authenticated():
            print("\nTaskBoard - Sign In")
            print("Type 'register' to create a new user account.")
            print("Type 'q' to quit the program.") #Codex generated quit feature

            email = prompt("Email: ").strip()
            if email.lower() == "register":
                self._sign_up_view.run()
                continue
            if email.lower() == "q":
                return False

            password = prompt_secret("Password: ")
            try:
                user = self._auth_service.sign_in(email=email, password=password)
                self._session_service.sign_in_user(user)
                print(f"Signed in as {user.first_name} {user.last_name}.")
            except AuthenticationError as error:
                print(f"Sign in failed: {error}")
        return True

    def show(self) -> bool:
        """Display sign-in view."""
        return self.run()
