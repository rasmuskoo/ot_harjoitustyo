"""Task repository for task-related database operations."""

from src.entities.task import Task
from src.repositories.database import get_database_connection


class TaskRepository:
    """Provides database operations for tasks and task participants."""

    def create_task(self, task: Task) -> Task:
        """Insert a new task.

        Args:
            task: Task data to store.

        Returns:
            Stored task with a database id.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title,
                    description,
                    created_by_user_id,
                    project_id,
                    priority,
                    due_date,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.created_by_user_id,
                    task.project_id,
                    task.priority,
                    task.due_date,
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
            priority=task.priority,
            due_date=task.due_date,
            project_id=task.project_id,
        )

    def add_participant(self, task_id: int, user_id: int) -> None:
        """Link a user as participant of a task.

        Args:
            task_id: Id of the task receiving the participant.
            user_id: Id of the user being added.
        """
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
        """Return active tasks where the user is a participant.

        Args:
            user_id: Id of the user whose active tasks are listed.

        Returns:
            Active tasks visible to the user.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
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
                    priority=row[5],
                    due_date=row[6],
                    project_id=row[7],
                    is_completed=bool(row[8]),
                )
            )
        return tasks

    def list_completed_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return completed tasks where the user is a participant.

        Args:
            user_id: Id of the user whose completed tasks are listed.

        Returns:
            Completed tasks visible to the user.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
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
                    priority=row[5],
                    due_date=row[6],
                    project_id=row[7],
                    is_completed=bool(row[8]),
                )
            )
        return tasks

    def list_all_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return all tasks where the user is a participant.

        Args:
            user_id: Id of the user whose task participation is listed.

        Returns:
            Active and completed tasks visible to the user.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                ORDER BY t.created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                created_by_user_id=row[3],
                created_at=row[4],
                priority=row[5],
                due_date=row[6],
                project_id=row[7],
                is_completed=bool(row[8]),
            )
            for row in rows
        ]

    def search_tasks_for_user(self, user_id: int, query: str) -> list[Task]:
        """Return user-visible tasks matching title or description.

        Args:
            user_id: Id of the user whose visible tasks are searched.
            query: Search keyword matched against task title and description.

        Returns:
            Tasks visible to the user whose title or description contains query.
        """
        search_pattern = f"%{query}%"
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                  AND (
                      t.title LIKE ? COLLATE NOCASE
                      OR t.description LIKE ? COLLATE NOCASE
                  )
                ORDER BY t.created_at DESC
                """,
                (user_id, search_pattern, search_pattern),
            )
            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                created_by_user_id=row[3],
                created_at=row[4],
                priority=row[5],
                due_date=row[6],
                project_id=row[7],
                is_completed=bool(row[8]),
            )
            for row in rows
        ]

    def find_task_for_user(self, task_id: int, user_id: int) -> Task | None:
        """Return one task if the user is a participant.

        Args:
            task_id: Id of the task being fetched.
            user_id: Id of the user requesting the task.

        Returns:
            Matching task, or None when the user cannot access it.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
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
            priority=row[5],
            due_date=row[6],
            project_id=row[7],
            is_completed=bool(row[8]),
        )

    def update_task_for_user(
        self,
        task_id: int,
        user_id: int,
        title: str,
        description: str,
    ) -> bool:
        """Update a task title and description if user is a participant.

        Args:
            task_id: Id of the task being updated.
            user_id: Id of the user requesting the update.
            title: New task title.
            description: New task description.

        Returns:
            True when the task was updated, otherwise False.
        """
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
        """Mark a task completed if the user is a participant.

        Args:
            task_id: Id of the task to complete.
            user_id: Id of the user requesting completion.

        Returns:
            True when the task was completed, otherwise False.
        """
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
        """Delete a task if the user is a participant.

        Args:
            task_id: Id of the task to delete.
            user_id: Id of the user requesting deletion.

        Returns:
            True when the task was deleted, otherwise False.
        """
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
                DELETE FROM task_labels
                WHERE task_id = ?
                """,
                (task_id,),
            )
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

    def add_participants(self, task_id: int, user_ids: list[int]) -> None:
        """Attach many users to a task participant list.

        Args:
            task_id: Id of the task receiving participants.
            user_ids: User ids to attach to the task.
        """
        if not user_ids:
            return

        with get_database_connection() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO task_participants (task_id, user_id)
                VALUES (?, ?)
                """,
                [(task_id, user_id) for user_id in user_ids],
            )
            connection.commit()

    def list_unassigned_tasks_for_user(self, user_id: int) -> list[Task]:
        """Return visible tasks that are not yet linked to a project.

        Args:
            user_id: Id of the user whose tasks are listed.

        Returns:
            User-visible tasks without a project link.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    t.id,
                    t.title,
                    t.description,
                    t.created_by_user_id,
                    t.created_at,
                    t.priority,
                    t.due_date,
                    t.project_id,
                    t.is_completed
                FROM tasks t
                INNER JOIN task_participants tp ON tp.task_id = t.id
                WHERE tp.user_id = ?
                  AND t.project_id IS NULL
                ORDER BY t.created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                created_by_user_id=row[3],
                created_at=row[4],
                priority=row[5],
                due_date=row[6],
                project_id=row[7],
                is_completed=bool(row[8]),
            )
            for row in rows
        ]

    def assign_task_to_project_for_user(self, task_id: int, project_id: int, user_id: int) -> bool:
        """Link a task to a project if the user is already a participant.

        Args:
            task_id: Id of the task being linked.
            project_id: Id of the target project.
            user_id: Id of the user requesting the change.

        Returns:
            True when the task was linked, otherwise False.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET project_id = ?
                WHERE id = ?
                  AND project_id IS NULL
                  AND EXISTS (
                      SELECT 1
                      FROM task_participants
                      WHERE task_id = tasks.id AND user_id = ?
                  )
                """,
                (project_id, task_id, user_id),
            )
            connection.commit()
        return cursor.rowcount > 0
