from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED


class IssueStatus(Base):
    __tablename__ = "issue_status"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{STATUS_NOT_RESOLVED}', '{STATUS_ACKNOWLEDGED}', '{STATUS_RESOLVED}')",
            name="ck_issue_status_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    row_index: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    ict_member_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resolution_remark: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{STATUS_NOT_RESOLVED}', '{STATUS_ACKNOWLEDGED}', '{STATUS_RESOLVED}')",
            name="ck_complaints_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    sheet_timestamp: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(320), nullable=False, default="")
    floor: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    room: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    ssid: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    issue_type: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    cluster_key: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_NOT_RESOLVED)
    ict_member_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resolution_remark: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
