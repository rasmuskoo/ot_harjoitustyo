"""Task repository for task-related database operations."""

from src.entities.task import Task
from src.repositories.database import get_database_connection


class TaskRepository:
    """Provides task persistence operations."""

    def create_task(self, task: Task) -> Task:
        """Insert a new task and return it with generated id."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title,
                    description,
                    created_by_user_id,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.created_by_user_id,
                    task.created_at,
                ),
            )
            connection.commit()

        return Task(
            id=cursor.lastrowid,
            title=task.title,
            description=task.description,
            created_by_user_id=task.created_by_user_id,
            created_at=task.created_at,
        )

    def add_participant(self, task_id: int, user_id: int) -> None:
        """Link a user as participant of a task."""
        with get_database_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO task_participants (task_id, user_id)
                VALUES (?, ?)
                """,
                (task_id, user_id),
            )
            connection.commit()

    def list_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return tasks where the user is a listed participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.created_by_user_id, t.created_at
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                ORDER BY t.created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        tasks: list[Task] = []
        for row in rows:
            tasks.append(
                Task(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    created_by_user_id=row[3],
                    created_at=row[4],
                )
            )
        return tasks
