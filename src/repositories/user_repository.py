"""User repository for database operations."""

from src.entities.user import User
from src.repositories.database import get_database_connection


class UserRepository:
    """Provides persistence operations for users."""

    def create_user(self, user: User) -> User:
        """Insert a new user and return it with generated id."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (first_name, last_name, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.password_hash,
                    user.created_at,
                ),
            )
            connection.commit()

        return User(
            id=cursor.lastrowid,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )

    def find_by_email(self, email: str) -> User | None:
        """Find one user by email."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, first_name, last_name, email, password_hash, created_at
                FROM users
                WHERE email = ?
                """,
                (email,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            password_hash=row[4],
            created_at=row[5],
        )
