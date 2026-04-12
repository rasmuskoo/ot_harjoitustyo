"""Authentication and account registration services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
import secrets

from src.entities.user import User
from src.repositories.user_repository import UserRepository


class RegistrationError(Exception):
    """Raised when user registration validation fails."""


class AuthenticationError(Exception):
    """Raised when sign-in authentication fails."""


@dataclass
class RegistrationInput:
    """Registration payload for creating a new user account."""

    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class AuthService:
    """Handles authentication-related application logic."""

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        """Create an auth service with an optional repository dependency."""
        self._user_repository = user_repository or UserRepository()

    def register(self, registration: RegistrationInput) -> User:
        """Validate input, create a new user, and return the stored user."""
        normalized_first_name = registration.first_name.strip()
        normalized_last_name = registration.last_name.strip()
        normalized_email = registration.email.strip().lower()

        self._validate_required_fields(registration)
        self._validate_email(normalized_email)
        self._validate_password(registration.password, registration.confirm_password)
        self._validate_unique_email(normalized_email)

        user = User(
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            email=normalized_email,
            password_hash=self._hash_password(registration.password),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return self._user_repository.create_user(user)

    def sign_in(self, email: str, password: str) -> User:
        """Authenticate user by email and password and return the user."""
        normalized_email = email.strip().lower()
        if not normalized_email or not password:
            raise AuthenticationError("Email and password are required.")

        user = self._user_repository.find_by_email(normalized_email)
        if user is None:
            raise AuthenticationError("Invalid email or password.")

        if not self._verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        return user

    def _validate_required_fields(self, registration: RegistrationInput) -> None:
        """Ensure all registration fields are present."""
        if not registration.first_name.strip():
            raise RegistrationError("First name is required.")
        if not registration.last_name.strip():
            raise RegistrationError("Last name is required.")
        if not registration.email.strip():
            raise RegistrationError("Email is required.")
        if not registration.password:
            raise RegistrationError("Password is required.")
        if not registration.confirm_password:
            raise RegistrationError("Confirm password is required.")

    def _validate_email(self, email: str) -> None:
        """Ensure email has a basic valid format."""
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if re.match(pattern, email) is None:
            raise RegistrationError("Email format is invalid.")

    def _validate_password(self, password: str, confirm_password: str) -> None:
        """Ensure password requirements are met."""
        if password != confirm_password:
            raise RegistrationError("Passwords do not match.")
        if len(password) < 8:
            raise RegistrationError("Password must be at least 8 characters long.")

    def _validate_unique_email(self, email: str) -> None:
        """Ensure the email is not already registered."""
        if self._user_repository.find_by_email(email) is not None:
            raise RegistrationError("Email is already registered.")

    def _hash_password(self, password: str) -> str:
        """Hash password using PBKDF2-HMAC-SHA256 and a per-user salt."""
        salt = secrets.token_hex(16)
        hashed_password = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return f"{salt}${hashed_password}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against the stored salt$hash representation."""
        try:
            salt, expected_hash = stored_hash.split("$", maxsplit=1)
        except ValueError:
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return secrets.compare_digest(actual_hash, expected_hash)
