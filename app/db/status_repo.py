from app.db.database import get_connection

ALLOWED_STATUSES = {"Resolved", "Not Resolved"}


def get_status(row_index: int) -> str:
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT status FROM issue_status WHERE row_index = ?",
            (row_index,),
        )
        row = cursor.fetchone()

    if row is None:
        return "Not Resolved"

    return str(row[0])


def get_status_map(row_indexes: list[int]) -> dict[int, str]:
    if not row_indexes:
        return {}

    placeholders = ",".join("?" for _ in row_indexes)
    query = f"SELECT row_index, status FROM issue_status WHERE row_index IN ({placeholders})"

    with get_connection() as connection:
        cursor = connection.execute(query, row_indexes)
        rows = cursor.fetchall()

    return {int(row[0]): str(row[1]) for row in rows}


def update_or_insert_status(row_index: int, status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO issue_status (row_index, status)
            VALUES (?, ?)
            ON CONFLICT(row_index) DO UPDATE SET status = excluded.status
            """,
            (row_index, status),
        )
        connection.commit()


def upsert_status(row_index: int, status: str) -> None:
    # Backward-compatible alias.
    update_or_insert_status(row_index=row_index, status=status)
