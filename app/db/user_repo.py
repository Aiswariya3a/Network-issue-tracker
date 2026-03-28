from typing import Any

from app.db.database import get_connection


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": int(row[0]),
        "username": str(row[1]),
        "password_hash": str(row[2]),
        "role": str(row[3]),
    }


def create_user_if_missing(username: str, password_hash: str, role: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO NOTHING
            """,
            (username, password_hash, role),
        )
        connection.commit()
