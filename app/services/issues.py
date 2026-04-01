import logging
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.core.config import settings
from app.db.database import get_session
from app.db.orm_models import Complaint
from app.db.status_repo import get_status_details, update_status
from app.models.issue import Issue
from app.models.status import (
    ALLOWED_STATUSES,
    STATUS_ACKNOWLEDGED,
    STATUS_NOT_RESOLVED,
    STATUS_RESOLVED,
)
from app.services.complaint_sync import sync_complaints
from app.services.resolution_email import send_status_email
from app.services.sheets import fetch_issues

logger = logging.getLogger(__name__)
OPEN_STATUSES = {STATUS_NOT_RESOLVED, STATUS_ACKNOWLEDGED}

ALLOWED_TRANSITIONS = {
    STATUS_NOT_RESOLVED: {STATUS_ACKNOWLEDGED, STATUS_RESOLVED},
    STATUS_ACKNOWLEDGED: {STATUS_RESOLVED, STATUS_NOT_RESOLVED},
    STATUS_RESOLVED: set(),
}


def _local_day_bounds(target_day: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(settings.scheduler_timezone)
    start_local = datetime.combine(target_day, time.min).replace(tzinfo=tz)
    end_local = datetime.combine(target_day, time.max).replace(tzinfo=tz)
    return (start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc))


def _today_local_date() -> date:
    return datetime.now(ZoneInfo(settings.scheduler_timezone)).date()


def _to_utc_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        # DB timestamps may be stored as naive UTC datetimes.
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_issue(complaint: Complaint) -> Issue:
    return Issue(
        row_index=int(complaint.id),
        complaint_key=complaint.complaint_key,
        timestamp=complaint.sheet_timestamp or "",
        email=complaint.email or "",
        floor=complaint.floor or "",
        room=complaint.room or "",
        ssid=complaint.ssid or "",
        location=complaint.location or "",
        issue_type=complaint.issue_type or "",
        description=complaint.description or "",
        cluster_key=complaint.cluster_key or "",
        status=str(complaint.status),
        ict_member_name=complaint.ict_member_name,
        resolution_remark=complaint.resolution_remark,
        acknowledged_at=complaint.acknowledged_at,
        resolved_at=complaint.resolved_at,
    )


def get_all_issues() -> list[Issue]:
    # Best-effort sync from the sheet; UI should still work from DB if sheet is temporarily unavailable.
    try:
        issues = fetch_issues()
        sync_complaints(issues)
    except Exception as exc:
        logger.warning("Sheet sync skipped while building issues list: %s", exc)

    today_local = _today_local_date()
    day_start_utc, day_end_utc = _local_day_bounds(today_local)

    with get_session() as session:
        complaints = session.execute(select(Complaint).order_by(Complaint.created_at.desc())).scalars().all()

    visible = [
        complaint
        for complaint in complaints
        if (
            complaint.status in OPEN_STATUSES
            or ((created_at_utc := _to_utc_aware(complaint.created_at)) is not None and day_start_utc <= created_at_utc <= day_end_utc)
        )
    ]
    return [_to_issue(complaint) for complaint in visible]


def update_issue_status(
    row_index: int,
    status: str,
    ict_member_name: str | None,
    resolution_remark: str | None = None,
) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Status must be one of: NOT RESOLVED, ACKNOWLEDGED, RESOLVED.")
    if row_index < 1:
        raise LookupError("Invalid complaint id.")

    with get_session() as session:
        complaint = session.execute(select(Complaint).where(Complaint.id == row_index)).scalar_one_or_none()
    if complaint is None:
        raise LookupError(f"Complaint {row_index} was not found.")

    complaint_key = complaint.complaint_key
    issue = _to_issue(complaint)
    existing = get_status_details(complaint_key=complaint_key)
    existing_status = str(existing["status"])
    if existing_status == status:
        raise ValueError(f"Complaint {row_index} is already in status '{status}'.")

    allowed_next = ALLOWED_TRANSITIONS.get(existing_status, set())
    if status not in allowed_next:
        raise ValueError(f"Invalid status transition: {existing_status} -> {status}.")

    if not ict_member_name:
        raise ValueError("ict_member_name is required.")
    if status == STATUS_ACKNOWLEDGED and not resolution_remark:
        raise ValueError("resolution_remark is required for ACKNOWLEDGED.")

    now = datetime.now(timezone.utc)
    acknowledged_at = existing["acknowledged_at"]
    resolved_at = existing["resolved_at"]

    if status == STATUS_ACKNOWLEDGED:
        acknowledged_at = now
        resolved_at = None
    elif status == STATUS_RESOLVED:
        if acknowledged_at is None:
            acknowledged_at = now
        resolved_at = now
    elif status == STATUS_NOT_RESOLVED:
        resolved_at = None

    update_status(
        complaint_key=complaint_key,
        status=status,
        ict_member_name=ict_member_name,
        resolution_remark=resolution_remark,
        acknowledged_at=acknowledged_at,
        resolved_at=resolved_at,
    )

    if status in {STATUS_ACKNOWLEDGED, STATUS_RESOLVED}:
        send_status_email(
            issue=issue,
            status=status,
            ict_member_name=ict_member_name or "",
            resolution_remark=resolution_remark,
        )
