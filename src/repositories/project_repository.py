"""Project repository for project-related database operations."""

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.database import get_database_connection


class ProjectRepository:
    """Provides project persistence operations."""

    def create_project(self, project: Project) -> Project:
        """Insert a new project and return it with generated id."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO projects (name, created_by_user_id, created_at)
                VALUES (?, ?, ?)
                """,
                (project.name, project.created_by_user_id, project.created_at),
            )
            connection.commit()

        return Project(
            id=cursor.lastrowid,
            name=project.name,
            created_by_user_id=project.created_by_user_id,
            created_at=project.created_at,
        )

    def add_member(self, project_id: int, user_id: int) -> None:
        """Attach a user to a project."""
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
        """Return projects where the user is a member."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT p.id, p.name, p.created_by_user_id, p.created_at
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
                created_at=row[3],
            )
            for row in rows
        ]

    def find_project_for_user(self, project_id: int, user_id: int) -> Project | None:
        """Return one project if the user is a member."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT p.id, p.name, p.created_by_user_id, p.created_at
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
            created_at=row[3],
        )

    def list_members(self, project_id: int) -> list[User]:
        """Return project members ordered by name."""
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
        """Return tasks linked to a project."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    created_by_user_id,
                    created_at,
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
                project_id=row[5],
                is_completed=bool(row[6]),
            )
            for row in rows
        ]

    def delete_project_for_user(self, project_id: int, user_id: int) -> bool:
        """Delete a project if the given user is its creator."""
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
