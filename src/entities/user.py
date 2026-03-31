"""User entity."""

from dataclasses import dataclass


@dataclass
class User:
    """Represents an application user."""

    first_name: str
    last_name: str
    email: str
    password_hash: str
    created_at: str
    id: int | None = None
