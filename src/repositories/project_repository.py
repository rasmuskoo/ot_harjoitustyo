"""Project repository for project-related database operations."""

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.database import get_database_connection


class ProjectRepository:
    """Provides database operations for projects and project membership."""

    def create_project(self, project: Project) -> Project:
        """Insert a new project.

        Args:
            project: Project data to store.

        Returns:
            Stored project with a database id.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO projects (name, created_by_user_id, priority, due_date, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    project.name,
                    project.created_by_user_id,
                    project.priority,
                    project.due_date,
                    project.created_at,
                ),
            )
            connection.commit()

        return Project(
            id=cursor.lastrowid,
            name=project.name,
            created_by_user_id=project.created_by_user_id,
            priority=project.priority,
            due_date=project.due_date,
            created_at=project.created_at,
        )

    def add_member(self, project_id: int, user_id: int) -> None:
        """Attach a user to a project.

        Args:
            project_id: Id of the project receiving the member.
            user_id: Id of the user being added.
        """
        with get_database_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO project_members (project_id, user_id)
                VALUES (?, ?)
                """,
                (project_id, user_id),
            )
            connection.commit()

    def list_projects_for_user(self, user_id: int) -> list[Project]:
        """Return projects where the user is a member.

        Args:
            user_id: Id of the user whose projects are listed.

        Returns:
            Projects visible to the user.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT p.id, p.name, p.created_by_user_id, p.priority, p.due_date, p.created_at
                FROM projects p
                INNER JOIN project_members pm ON pm.project_id = p.id
                WHERE pm.user_id = ?
                ORDER BY p.created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        return [
            Project(
                id=row[0],
                name=row[1],
                created_by_user_id=row[2],
                priority=row[3],
                due_date=row[4],
                created_at=row[5],
            )
            for row in rows
        ]

    def search_projects_for_user(self, user_id: int, query: str) -> list[Project]:
        """Return user-visible projects matching name.

        Args:
            user_id: Id of the user whose visible projects are searched.
            query: Search keyword matched against project name.

        Returns:
            Projects visible to the user whose name contains query.
        """
        search_pattern = f"%{query}%"
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT p.id, p.name, p.created_by_user_id, p.priority, p.due_date, p.created_at
                FROM projects p
                INNER JOIN project_members pm ON pm.project_id = p.id
                WHERE pm.user_id = ?
                  AND p.name LIKE ? COLLATE NOCASE
                ORDER BY p.created_at DESC
                """,
                (user_id, search_pattern),
            )
            rows = cursor.fetchall()

        return [
            Project(
                id=row[0],
                name=row[1],
                created_by_user_id=row[2],
                priority=row[3],
                due_date=row[4],
                created_at=row[5],
            )
            for row in rows
        ]

    def find_project_for_user(self, project_id: int, user_id: int) -> Project | None:
        """Return one project if the user is a member.

        Args:
            project_id: Id of the project being fetched.
            user_id: Id of the user requesting the project.

        Returns:
            Matching project, or None when the user cannot access it.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT p.id, p.name, p.created_by_user_id, p.priority, p.due_date, p.created_at
                FROM projects p
                INNER JOIN project_members pm ON pm.project_id = p.id
                WHERE p.id = ? AND pm.user_id = ?
                """,
                (project_id, user_id),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Project(
            id=row[0],
            name=row[1],
            created_by_user_id=row[2],
            priority=row[3],
            due_date=row[4],
            created_at=row[5],
        )

    def list_members(self, project_id: int) -> list[User]:
        """Return project members ordered by name.

        Args:
            project_id: Id of the project whose members are listed.

        Returns:
            Users who belong to the project.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT u.id, u.first_name, u.last_name, u.email, u.password_hash, u.created_at
                FROM users u
                INNER JOIN project_members pm ON pm.user_id = u.id
                WHERE pm.project_id = ?
                ORDER BY u.first_name, u.last_name, u.email
                """,
                (project_id,),
            )
            rows = cursor.fetchall()

        return [
            User(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                password_hash=row[4],
                created_at=row[5],
            )
            for row in rows
        ]

    def list_tasks(self, project_id: int) -> list[Task]:
        """Return tasks linked to a project.

        Args:
            project_id: Id of the project whose tasks are listed.

        Returns:
            Tasks linked to the project.
        """
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    created_by_user_id,
                    created_at,
                    priority,
                    due_date,
                    project_id,
                    is_completed
                FROM tasks
                WHERE project_id = ?
                ORDER BY created_at DESC
                """,
                (project_id,),
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

    def delete_project_for_user(self, project_id: int, user_id: int) -> bool:
        """Delete a project if the given user is its creator.

        Args:
            project_id: Id of the project to delete.
            user_id: Id of the user requesting deletion.

        Returns:
            True when the project was deleted, otherwise False.
        """
        with get_database_connection() as connection:
            permission_cursor = connection.execute(
                """
                SELECT 1
                FROM projects
                WHERE id = ? AND created_by_user_id = ?
                """,
                (project_id, user_id),
            )
            if permission_cursor.fetchone() is None:
                return False

            connection.execute(
                """
                UPDATE tasks
                SET project_id = NULL
                WHERE project_id = ?
                """,
                (project_id,),
            )
            connection.execute(
                """
                DELETE FROM project_members
                WHERE project_id = ?
                """,
                (project_id,),
            )
            delete_cursor = connection.execute(
                """
                DELETE FROM projects
                WHERE id = ?
                """,
                (project_id,),
            )
            connection.commit()
        return delete_cursor.rowcount > 0
