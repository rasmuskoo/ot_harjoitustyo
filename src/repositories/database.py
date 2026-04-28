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
        _create_tables(connection)
        _migrate_tasks(connection)
        _migrate_projects(connection)
        connection.commit()


def _create_tables(connection: sqlite3.Connection) -> None:
    """Create database tables when they do not exist."""
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
            project_id INTEGER,
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            is_completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by_user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by_user_id INTEGER NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by_user_id) REFERENCES users(id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS project_members (
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (project_id, user_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
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


def _migrate_tasks(connection: sqlite3.Connection) -> None:
    """Add missing task columns for existing databases."""
    column_names = _column_names(connection, "tasks")
    _add_column_if_missing(
        connection,
        column_names,
        "is_completed",
        "ALTER TABLE tasks ADD COLUMN is_completed INTEGER NOT NULL DEFAULT 0",
    )
    _add_column_if_missing(
        connection,
        column_names,
        "project_id",
        "ALTER TABLE tasks ADD COLUMN project_id INTEGER",
    )
    _add_column_if_missing(
        connection,
        column_names,
        "priority",
        "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'",
    )
    _add_column_if_missing(
        connection,
        column_names,
        "due_date",
        "ALTER TABLE tasks ADD COLUMN due_date TEXT",
    )


def _migrate_projects(connection: sqlite3.Connection) -> None:
    """Add missing project columns for existing databases."""
    column_names = _column_names(connection, "projects")
    _add_column_if_missing(
        connection,
        column_names,
        "priority",
        "ALTER TABLE projects ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'",
    )
    _add_column_if_missing(
        connection,
        column_names,
        "due_date",
        "ALTER TABLE projects ADD COLUMN due_date TEXT",
    )


def _column_names(connection: sqlite3.Connection, table_name: str) -> set[str]:
    """Return column names for a database table."""
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {column[1] for column in columns}


def _add_column_if_missing(
    connection: sqlite3.Connection,
    column_names: set[str],
    column_name: str,
    alter_table_sql: str,
) -> None:
    """Run an ALTER TABLE statement if the column is missing."""
    if column_name not in column_names:
        connection.execute(alter_table_sql)
