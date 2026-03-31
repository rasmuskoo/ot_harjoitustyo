"""Session state management for authenticated users."""

from src.entities.user import User


class SessionService:
    """Tracks current authentication session in application memory."""

    def __init__(self) -> None:
        """Initialize session as signed out."""
        self._current_user: User | None = None

    def sign_in_user(self, user: User) -> None:
        """Store authenticated user as current session user."""
        self._current_user = user

    def sign_out(self) -> None:
        """Clear current session user."""
        self._current_user = None

    def is_authenticated(self) -> bool:
        """Return whether a user is currently signed in."""
        return self._current_user is not None

    def get_current_user(self) -> User | None:
        """Return currently authenticated user, if any."""
        return self._current_user
