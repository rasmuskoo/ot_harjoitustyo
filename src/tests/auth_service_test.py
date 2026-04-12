import unittest

from src.entities.user import User
from src.services.auth_service import AuthenticationError, AuthService, RegistrationError


class FakeUserRepository:
    def __init__(self):
        self._users_by_email = {}
        self._next_id = 1

    def find_by_email(self, email: str):
        return self._users_by_email.get(email)

    def create_user(self, user: User):
        stored_user = User(
            id=self._next_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )
        self._users_by_email[stored_user.email] = stored_user
        self._next_id += 1
        return stored_user


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.user_repository = FakeUserRepository()
        self.auth_service = AuthService(self.user_repository)

    def test_registered_user_can_sign_in_with_same_credentials(self):
        registered_user = self.auth_service.register(
            first_name="Ada",
            last_name="Lovelace",
            email="Ada@Example.com",
            password="password123",
            confirm_password="password123",
        )

        signed_in_user = self.auth_service.sign_in(
            email="ada@example.com",
            password="password123",
        )

        self.assertEqual(registered_user.id, signed_in_user.id)
        self.assertEqual(signed_in_user.email, "ada@example.com")
        self.assertNotEqual(signed_in_user.password_hash, "password123")

    def test_sign_in_with_wrong_password_raises_error(self):
        self.auth_service.register(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="password123",
            confirm_password="password123",
        )

        with self.assertRaises(AuthenticationError):
            self.auth_service.sign_in(email="ada@example.com", password="wrongpassword")

    def test_register_with_duplicate_email_raises_error(self):
        self.auth_service.register(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="password123",
            confirm_password="password123",
        )

        with self.assertRaises(RegistrationError):
            self.auth_service.register(
                first_name="Another",
                last_name="User",
                email="ada@example.com",
                password="password123",
                confirm_password="password123",
            )

    def test_register_with_invalid_email_raises_error(self):
        with self.assertRaises(RegistrationError):
            self.auth_service.register(
                first_name="Ada",
                last_name="Lovelace",
                email="not-an-email",
                password="password123",
                confirm_password="password123",
            )

    def test_register_with_password_mismatch_raises_error(self):
        with self.assertRaises(RegistrationError):
            self.auth_service.register(
                first_name="Ada",
                last_name="Lovelace",
                email="ada@example.com",
                password="password123",
                confirm_password="differentpassword",
            )


if __name__ == "__main__":
    unittest.main()
