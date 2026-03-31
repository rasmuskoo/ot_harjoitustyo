"""Task repository for task-related database reads."""

from src.entities.task import Task
from src.repositories.database import get_database_connection


class TaskRepository:
    """Provides task queries for application views."""

    def list_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return tasks where the user is a listed participant."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT t.id, t.title, t.description, t.importance, t.due_date,
                       t.created_by_user_id, t.created_at
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
                    importance=row[3],
                    due_date=row[4],
                    created_by_user_id=row[5],
                    created_at=row[6],
                )
            )
        return tasks
