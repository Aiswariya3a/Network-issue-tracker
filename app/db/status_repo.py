from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.db.database import get_session
from app.db.orm_models import Complaint
from app.models.status import ALLOWED_STATUSES, STATUS_NOT_RESOLVED


def _status_record_or_default(record: Complaint | None) -> dict[str, Any]:
    if record is None:
        return {
            "status": STATUS_NOT_RESOLVED,
            "ict_member_name": None,
            "resolution_remark": None,
            "acknowledged_at": None,
            "resolved_at": None,
        }
    return {
        "status": str(record.status),
        "ict_member_name": record.ict_member_name,
        "resolution_remark": record.resolution_remark,
        "acknowledged_at": record.acknowledged_at,
        "resolved_at": record.resolved_at,
    }


def get_status_details(complaint_key: str) -> dict[str, Any]:
    with get_session() as session:
        record = session.execute(
            select(Complaint).where(Complaint.complaint_key == complaint_key)
        ).scalar_one_or_none()
    return _status_record_or_default(record)


def get_status_details_map(complaint_keys: list[str]) -> dict[str, dict[str, Any]]:
    if not complaint_keys:
        return {}

    with get_session() as session:
        rows = session.execute(select(Complaint).where(Complaint.complaint_key.in_(complaint_keys))).scalars().all()

    return {str(row.complaint_key): _status_record_or_default(row) for row in rows}


def update_status(
    complaint_key: str,
    status: str,
    ict_member_name: str | None,
    resolution_remark: str | None,
    acknowledged_at: datetime | None = None,
    resolved_at: datetime | None = None,
) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status.")

    with get_session() as session:
        complaint = session.execute(
            select(Complaint).where(Complaint.complaint_key == complaint_key)
        ).scalar_one_or_none()
        if complaint is None:
            raise LookupError("Complaint was not found in persistent storage. Run sync first.")

        complaint.status = status
        complaint.ict_member_name = ict_member_name
        complaint.resolution_remark = resolution_remark
        complaint.acknowledged_at = acknowledged_at
        complaint.resolved_at = resolved_at
        complaint.updated_at = datetime.now(timezone.utc)

        session.commit()
