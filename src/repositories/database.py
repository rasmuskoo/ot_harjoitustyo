"""Database setup and connection helpers."""

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "taskboard.db"


def get_database_connection() -> sqlite3.Connection:
    """SQLite connection to the app's database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def initialize_database() -> None:
    """Create required database tables if they do not exist."""
    with get_database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_by_user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (created_by_user_id) REFERENCES users(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS task_participants (
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        connection.commit()
