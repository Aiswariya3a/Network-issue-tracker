import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session

from app.db.database import Base
from app.db.orm_models import IssueStatus, User
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED


def _sqlite_url_from_path(path_value: str) -> str:
    sqlite_path = Path(path_value)
    if not sqlite_path.is_absolute():
        sqlite_path = (Path.cwd() / sqlite_path).resolve()
    return f"sqlite:///{sqlite_path.as_posix()}"


def main() -> None:
    sqlite_path = os.getenv("SOURCE_SQLITE_DB_PATH", os.getenv("SQLITE_DB_PATH", "issues.db"))
    postgres_url = os.getenv("TARGET_DATABASE_URL", os.getenv("DATABASE_URL", "")).strip()

    if not postgres_url:
        raise RuntimeError("Set TARGET_DATABASE_URL (or DATABASE_URL) to a PostgreSQL URL before running migration.")
    if not postgres_url.startswith("postgresql"):
        raise RuntimeError("TARGET_DATABASE_URL must be a PostgreSQL SQLAlchemy URL.")

    sqlite_engine = create_engine(_sqlite_url_from_path(sqlite_path))
    postgres_engine = create_engine(postgres_url)

    _ensure_issue_status_timestamps(sqlite_engine)
    Base.metadata.create_all(bind=postgres_engine)

    inserted_users = 0
    inserted_statuses = 0
    updated_statuses = 0

    with Session(sqlite_engine) as source_session, Session(postgres_engine) as target_session:
        source_users = source_session.execute(select(User)).scalars().all()
        source_statuses = source_session.execute(select(IssueStatus)).scalars().all()

        for src_user in source_users:
            existing_user = target_session.execute(
                select(User).where(User.username == src_user.username)
            ).scalar_one_or_none()
            if existing_user is None:
                target_session.add(
                    User(
                        username=src_user.username,
                        password_hash=src_user.password_hash,
                        role=src_user.role,
                    )
                )
                inserted_users += 1

        for src_status in source_statuses:
            existing_status = target_session.execute(
                select(IssueStatus).where(IssueStatus.row_index == src_status.row_index)
            ).scalar_one_or_none()
            if existing_status is None:
                normalized_status = _normalize_status(src_status.status)
                target_session.add(
                    IssueStatus(
                        row_index=src_status.row_index,
                        status=normalized_status,
                        ict_member_name=src_status.ict_member_name,
                        resolution_remark=src_status.resolution_remark,
                        acknowledged_at=src_status.acknowledged_at,
                        resolved_at=src_status.resolved_at,
                        created_at=src_status.created_at,
                        updated_at=src_status.updated_at,
                    )
                )
                inserted_statuses += 1
            elif existing_status.status != src_status.status:
                existing_status.status = _normalize_status(src_status.status)
                existing_status.ict_member_name = src_status.ict_member_name
                existing_status.resolution_remark = src_status.resolution_remark
                existing_status.acknowledged_at = src_status.acknowledged_at
                existing_status.resolved_at = src_status.resolved_at
                existing_status.updated_at = src_status.updated_at
                updated_statuses += 1

        target_session.commit()

    print("Migration complete.")
    print(f"Users inserted: {inserted_users}")
    print(f"Issue statuses inserted: {inserted_statuses}")
    print(f"Issue statuses updated: {updated_statuses}")

def _ensure_issue_status_timestamps(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "issue_status" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("issue_status")}
    statements: list[str] = []
    if "created_at" not in existing_columns:
        statements.append(
            "ALTER TABLE issue_status ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )
    if "updated_at" not in existing_columns:
        statements.append(
            "ALTER TABLE issue_status ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )
    if "ict_member_name" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN ict_member_name VARCHAR(128)")
    if "resolution_remark" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN resolution_remark VARCHAR(1000)")
    if "acknowledged_at" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN acknowledged_at TIMESTAMP")
    if "resolved_at" not in existing_columns:
        statements.append("ALTER TABLE issue_status ADD COLUMN resolved_at TIMESTAMP")

    if not statements:
        return

    with engine.begin() as connection:
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


def _normalize_status(value: str) -> str:
    if value == "Resolved":
        return STATUS_RESOLVED
    if value == "Not Resolved":
        return STATUS_NOT_RESOLVED
    if value in {STATUS_NOT_RESOLVED, STATUS_ACKNOWLEDGED, STATUS_RESOLVED}:
        return value
    return STATUS_NOT_RESOLVED


if __name__ == "__main__":
    main()
