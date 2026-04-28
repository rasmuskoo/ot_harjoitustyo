"""Label repository for label-related database operations."""

from src.entities.label import Label
from src.repositories.database import get_database_connection


class LabelRepository:
    """Provides label persistence operations."""

    def create_label(self, label: Label) -> Label:
        """Insert a new label and return it with generated id."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO labels (name)
                VALUES (?)
                """,
                (label.name,),
            )
            connection.commit()

        return Label(id=cursor.lastrowid, name=label.name)

    def find_by_name(self, name: str) -> Label | None:
        """Return one label by exact normalized name."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, name
                FROM labels
                WHERE name = ?
                """,
                (name,),
            )
            row = cursor.fetchone()

        if row is None:
            return None
        return Label(id=row[0], name=row[1])

    def find_by_id(self, label_id: int) -> Label | None:
        """Return one label by id."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, name
                FROM labels
                WHERE id = ?
                """,
                (label_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None
        return Label(id=row[0], name=row[1])

    def list_labels(self) -> list[Label]:
        """Return all labels ordered by name."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, name
                FROM labels
                ORDER BY name
                """
            )
            rows = cursor.fetchall()

        return [Label(id=row[0], name=row[1]) for row in rows]

    def search_labels(self, query: str) -> list[Label]:
        """Return labels whose names contain the query."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, name
                FROM labels
                WHERE name LIKE ?
                ORDER BY name
                """,
                (f"%{query}%",),
            )
            rows = cursor.fetchall()

        return [Label(id=row[0], name=row[1]) for row in rows]

    def add_label_to_task(self, task_id: int, label_id: int) -> None:
        """Attach a label to a task."""
        with get_database_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO task_labels (task_id, label_id)
                VALUES (?, ?)
                """,
                (task_id, label_id),
            )
            connection.commit()

    def list_labels_for_task(self, task_id: int) -> list[Label]:
        """Return labels attached to one task."""
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                SELECT l.id, l.name
                FROM labels l
                INNER JOIN task_labels tl ON tl.label_id = l.id
                WHERE tl.task_id = ?
                ORDER BY l.name
                """,
                (task_id,),
            )
            rows = cursor.fetchall()

        return [Label(id=row[0], name=row[1]) for row in rows]
