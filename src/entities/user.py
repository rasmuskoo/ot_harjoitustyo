"""User entity."""

from dataclasses import dataclass


@dataclass
class User:
    """Represents an application user.

    Attributes:
        first_name: User's first name.
        last_name: User's last name.
        email: Unique email address used for sign-in.
        password_hash: Stored password hash with salt.
        created_at: Creation time stored as an ISO formatted string.
        id: Database id for the user, or None before the user is stored.
    """

    first_name: str
    last_name: str
    email: str
    password_hash: str
    created_at: str
    id: int | None = None
