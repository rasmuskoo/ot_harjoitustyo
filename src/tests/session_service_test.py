"""Unit tests for session service."""

import unittest

from src.entities.user import User
from src.services.session_service import SessionService


class TestSessionService(unittest.TestCase):
    """Tests for authentication session state."""

    def setUp(self):
        """Create empty session service."""
        self.session_service = SessionService()
        self.user = User(
            id=1,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password_hash="hash",
            created_at="now",
        )

    def test_session_starts_signed_out(self):
        """New session should not be authenticated."""
        self.assertFalse(self.session_service.is_authenticated())
        self.assertIsNone(self.session_service.get_current_user())

    def test_sign_in_user_stores_current_user(self):
        """Signing in should store current user."""
        self.session_service.sign_in_user(self.user)

        self.assertTrue(self.session_service.is_authenticated())
        self.assertEqual(self.session_service.get_current_user(), self.user)

    def test_sign_out_clears_current_user(self):
        """Signing out should clear current user."""
        self.session_service.sign_in_user(self.user)

        self.session_service.sign_out()

        self.assertFalse(self.session_service.is_authenticated())
        self.assertIsNone(self.session_service.get_current_user())


if __name__ == "__main__":
    unittest.main()
