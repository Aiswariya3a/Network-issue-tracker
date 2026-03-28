import sqlite3

from app.core.config import settings


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(settings.sqlite_db_path)


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS issue_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                row_index INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL CHECK(status IN ('Resolved', 'Not Resolved'))
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        connection.commit()
