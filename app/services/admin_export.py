from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

from openpyxl import Workbook
from sqlalchemy import and_, or_, select

from app.core.config import settings
from app.db.database import get_session
from app.db.orm_models import Complaint
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_RESOLVED

MAX_EXPORT_WINDOW_DAYS = 30


def get_local_today() -> date:
    tz = ZoneInfo(settings.scheduler_timezone)
    return datetime.now(tz).date()


def validate_export_date_range(from_date: date, to_date: date) -> None:
    if to_date < from_date:
        raise ValueError("to_date must be on or after from_date.")

    today = get_local_today()
    min_date = today - timedelta(days=MAX_EXPORT_WINDOW_DAYS - 1)

    if from_date < min_date or to_date < min_date:
        raise ValueError("Date range must be within the last 30 days.")
    if from_date > today or to_date > today:
        raise ValueError("Date range cannot include future dates.")


def _fmt_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _local_range_to_utc(from_date: date, to_date: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(settings.scheduler_timezone)
    local_start = datetime.combine(from_date, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(to_date, time.max).replace(tzinfo=tz)
    return (local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc))


def build_admin_export_workbook(from_date: date, to_date: date) -> BytesIO:
    validate_export_date_range(from_date=from_date, to_date=to_date)

    from_dt, to_dt = _local_range_to_utc(from_date=from_date, to_date=to_date)

    with get_session() as session:
        rows = (
            session.execute(
                select(Complaint).where(
                    or_(
                        and_(
                            Complaint.status == STATUS_RESOLVED,
                            # Export resolved issues by resolution timestamp.
                            # Fallback to created_at for older rows that may miss resolved_at.
                            or_(
                                and_(Complaint.resolved_at.is_not(None), Complaint.resolved_at >= from_dt, Complaint.resolved_at <= to_dt),
                                and_(Complaint.resolved_at.is_(None), Complaint.created_at >= from_dt, Complaint.created_at <= to_dt),
                            ),
                        ),
                        and_(
                            Complaint.status == STATUS_ACKNOWLEDGED,
                            Complaint.created_at >= from_dt,
                            Complaint.created_at <= to_dt,
                        ),
                    )
                )
            )
            .scalars()
            .all()
        )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Complaints Report"

    headers = [
        "Complaint ID",
        "Title / Description",
        "Location (Floor, Room, SSID)",
        "User Email",
        "Status",
        "Resolution Note",
        "Resolved By (ICT Name)",
        "Created At",
        "Resolved At",
    ]
    sheet.append(headers)

    for complaint in rows:
        title_description = " | ".join(part for part in [complaint.issue_type, complaint.description] if part) or "-"
        location_block = " | ".join(part for part in [complaint.floor, complaint.room, complaint.ssid] if part) or "-"

        sheet.append(
            [
                complaint.id,
                title_description,
                location_block,
                complaint.email,
                complaint.status,
                complaint.resolution_remark or "",
                complaint.ict_member_name or "",
                _fmt_datetime(complaint.created_at),
                _fmt_datetime(complaint.resolved_at),
            ]
        )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
