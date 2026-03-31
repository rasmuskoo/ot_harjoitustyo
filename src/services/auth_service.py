"""Authentication and account registration services."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
import secrets

from src.entities.user import User
from src.repositories.user_repository import UserRepository


class RegistrationError(Exception):
    """Raised when user registration validation fails."""


class AuthService:
    """Handles authentication-related application logic."""

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        """Create an auth service with an optional repository dependency."""
        self._user_repository = user_repository or UserRepository()

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> User:
        """Validate input, create a new user, and return the stored user."""
        normalized_first_name = first_name.strip()
        normalized_last_name = last_name.strip()
        normalized_email = email.strip().lower()

        self._validate_required_fields(
            normalized_first_name,
            normalized_last_name,
            normalized_email,
            password,
            confirm_password,
        )
        self._validate_email(normalized_email)
        self._validate_password(password, confirm_password)
        self._validate_unique_email(normalized_email)

        user = User(
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            email=normalized_email,
            password_hash=self._hash_password(password),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return self._user_repository.create_user(user)

    def _validate_required_fields(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> None:
        """Ensure all registration fields are present."""
        if not first_name:
            raise RegistrationError("First name is required.")
        if not last_name:
            raise RegistrationError("Last name is required.")
        if not email:
            raise RegistrationError("Email is required.")
        if not password:
            raise RegistrationError("Password is required.")
        if not confirm_password:
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
