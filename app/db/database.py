from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


DATABASE_URL = settings.database_url.strip()
if not DATABASE_URL.startswith("postgresql"):
    raise RuntimeError(
        "DATABASE_URL must be a PostgreSQL SQLAlchemy URL, for example: "
        "postgresql+psycopg2://user:password@host:5432/dbname"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    # Import models so SQLAlchemy knows table metadata before create_all.
    from app.db import orm_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_backward_compatible_migrations()


def _apply_backward_compatible_migrations() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "issue_status" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("issue_status")}
    statements: list[str] = []

    if "created_at" not in existing_columns:
        statements.append(
            "ALTER TABLE issue_status ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT NOW()"
        )
    if "updated_at" not in existing_columns:
        statements.append(
            "ALTER TABLE issue_status ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW()"
        )
    if "ict_member_name" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN ict_member_name VARCHAR(128)")
    if "resolution_remark" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN resolution_remark VARCHAR(1000)")
    if "acknowledged_at" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN acknowledged_at TIMESTAMP")
    if "resolved_at" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN resolved_at TIMESTAMP")

    with engine.begin() as connection:
        # Normalize legacy values before enforcing the new check constraint.
        connection.execute(
            text(
                """
                UPDATE issue_status
                SET status = CASE
                    WHEN status = 'Resolved' THEN 'RESOLVED'
                    WHEN status = 'Not Resolved' THEN 'NOT RESOLVED'
                    ELSE status
                END
                """
            )
        )

        for statement in statements:
            connection.execute(text(statement))

        connection.execute(text("ALTER TABLE issue_status DROP CONSTRAINT IF EXISTS ck_issue_status_status"))
        connection.execute(
            text(
                """
                ALTER TABLE issue_status
                ADD CONSTRAINT ck_issue_status_status
                CHECK (status IN ('NOT RESOLVED', 'ACKNOWLEDGED', 'RESOLVED'))
                """
            )
        )
