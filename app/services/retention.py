import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select

from app.db.database import get_session
from app.db.orm_models import ArchivedComplaint, Complaint
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_RESOLVED

logger = logging.getLogger(__name__)


def cleanup_old_complaints(retention_days: int, archive_before_delete: bool = True) -> dict[str, int]:
    if retention_days <= 0:
        raise ValueError("retention_days must be a positive integer.")

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    with get_session() as session:
        candidates = (
            session.execute(
                select(Complaint).where(
                    and_(
                        Complaint.status.in_([STATUS_ACKNOWLEDGED, STATUS_RESOLVED]),
                        Complaint.created_at < cutoff,
                    )
                )
            )
            .scalars()
            .all()
        )

        if not candidates:
            return {"archived": 0, "deleted": 0}

        archived_count = 0
        if archive_before_delete:
            existing_archived_ids = {
                row[0]
                for row in session.execute(
                    select(ArchivedComplaint.original_complaint_id).where(
                        ArchivedComplaint.original_complaint_id.in_([item.id for item in candidates])
                    )
                ).all()
            }

            for complaint in candidates:
                if complaint.id in existing_archived_ids:
                    continue
                session.add(
                    ArchivedComplaint(
                        original_complaint_id=complaint.id,
                        complaint_key=complaint.complaint_key,
                        sheet_timestamp=complaint.sheet_timestamp,
                        email=complaint.email,
                        floor=complaint.floor,
                        room=complaint.room,
                        ssid=complaint.ssid,
                        location=complaint.location,
                        issue_type=complaint.issue_type,
                        description=complaint.description,
                        cluster_key=complaint.cluster_key,
                        status=complaint.status,
                        ict_member_name=complaint.ict_member_name,
                        resolution_remark=complaint.resolution_remark,
                        acknowledged_at=complaint.acknowledged_at,
                        resolved_at=complaint.resolved_at,
                        created_at=complaint.created_at,
                        updated_at=complaint.updated_at,
                    )
                )
                archived_count += 1

        for complaint in candidates:
            session.delete(complaint)

        session.commit()
        deleted_count = len(candidates)

    logger.info(
        "Retention cleanup finished. cutoff=%s archived=%s deleted=%s",
        cutoff.isoformat(),
        archived_count,
        deleted_count,
    )
    return {"archived": archived_count, "deleted": deleted_count}
