"""Session state management for authenticated users."""

from src.entities.user import User


class SessionService:
    """Tracks the current authentication session in memory."""

    def __init__(self) -> None:
        """Create an empty signed-out session."""
        self._current_user: User | None = None

    def sign_in_user(self, user: User) -> None:
        """Store an authenticated user as the current user.

        Args:
            user: User returned by successful authentication.
        """
        self._current_user = user

    def sign_out(self) -> None:
        """Clear the current user from the session."""
        self._current_user = None

    def is_authenticated(self) -> bool:
        """Return whether a user is currently signed in.

        Returns:
            True when a current user exists, otherwise False.
        """
        return self._current_user is not None

    def get_current_user(self) -> User | None:
        """Return the current user.

        Returns:
            Current user, or None when signed out.
        """
        return self._current_user
