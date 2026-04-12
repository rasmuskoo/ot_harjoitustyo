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
        """Return active tasks where the user is a listed participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.created_by_user_id, t.created_at, t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                  AND t.is_completed = 0
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
                    is_completed=bool(row[5]),
                )
            )
        return tasks

    def list_completed_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return completed tasks where the user is a listed participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.created_by_user_id, t.created_at, t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                  AND t.is_completed = 1
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
                    is_completed=bool(row[5]),
                )
            )
        return tasks

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        """Return one task if the user is a participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.created_by_user_id, t.created_at, t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE t.id = ? AND tp.user_id = ?
                """,
                (task_id, user_id),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            created_by_user_id=row[3],
            created_at=row[4],
            is_completed=bool(row[5]),
        )

    def update_task_for_user(self, task_id: int, user_id: int, title: str, description: str) -> bool:
        """Update a task header and description if the user is a participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?
                WHERE id = ?
                  AND EXISTS (
                      SELECT 1
                      FROM task_participants
                      WHERE task_id = tasks.id AND user_id = ?
                  )
                """,
                (title, description, task_id, user_id),
            )
            connection.commit()
        return cursor.rowcount > 0

    def complete_task_for_user(self, task_id: int, user_id: int) -> bool:
        """Mark a task completed if the user is a participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET is_completed = 1
                WHERE id = ?
                  AND is_completed = 0
                  AND EXISTS (
                      SELECT 1
                      FROM task_participants
                      WHERE task_id = tasks.id AND user_id = ?
                  )
                """,
                (task_id, user_id),
            )
            connection.commit()
        return cursor.rowcount > 0

    def delete_task_for_user(self, task_id: int, user_id: int) -> bool:
        """Delete a task if the user is a participant."""
        with get_database_connection() as connection:
            permission_cursor = connection.execute(
                """
                SELECT 1
                FROM task_participants
                WHERE task_id = ? AND user_id = ?
                """,
                (task_id, user_id),
            )
            if permission_cursor.fetchone() is None:
                return False

            connection.execute(
                """
                DELETE FROM task_participants
                WHERE task_id = ?
                """,
                (task_id,),
            )
            delete_cursor = connection.execute(
                """
                DELETE FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            )
            connection.commit()
        return delete_cursor.rowcount > 0

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        """Return one task if the user is a participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.created_by_user_id, t.created_at
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE t.id = ? AND tp.user_id = ?
                """,
                (task_id, user_id),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            created_by_user_id=row[3],
            created_at=row[4],
        )

    def update_task_for_user(self, task_id: int, user_id: int, title: str, description: str) -> bool:
        """Update a task if the user is a participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?
                WHERE id = ?
                  AND EXISTS (
                      SELECT 1
                      FROM task_participants
                      WHERE task_id = tasks.id AND user_id = ?
                  )
                """,
                (title, description, task_id, user_id),
            )
            connection.commit()
        return cursor.rowcount > 0
