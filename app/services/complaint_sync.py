import hashlib
import logging
import re
from collections.abc import Iterable

from sqlalchemy import select

from app.db.database import get_session
from app.db.orm_models import Complaint
from app.models.issue import Issue
from app.models.status import STATUS_NOT_RESOLVED
from app.services.sheets import fetch_issues

logger = logging.getLogger(__name__)
_MULTISPACE = re.compile(r"\s+")


def _norm(value: str) -> str:
    return _MULTISPACE.sub(" ", (value or "").strip()).casefold()


def build_complaint_key(issue: Issue) -> str:
    # Stable business key from sheet payload fields; ignores row_index because sheet resets daily.
    payload = "|".join(
        [
            _norm(issue.timestamp),
            _norm(issue.email),
            _norm(issue.location),
            _norm(issue.issue_type),
            _norm(issue.description),
            _norm(issue.cluster_key),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _insert_new_complaints(issues: Iterable[Issue]) -> tuple[int, int]:
    issues_list = list(issues)
    if not issues_list:
        return (0, 0)

    keyed_issues: list[tuple[str, Issue]] = [(build_complaint_key(issue), issue) for issue in issues_list]
    unique_keys = {key for key, _ in keyed_issues}

    with get_session() as session:
        existing_keys = {
            row[0]
            for row in session.execute(
                select(Complaint.complaint_key).where(Complaint.complaint_key.in_(unique_keys))
            ).all()
        }

        inserted = 0
        duplicates = 0
        for complaint_key, issue in keyed_issues:
            if complaint_key in existing_keys:
                duplicates += 1
                continue

            session.add(
                Complaint(
                    complaint_key=complaint_key,
                    sheet_timestamp=issue.timestamp,
                    email=issue.email,
                    floor=issue.floor,
                    room=issue.room,
                    ssid=issue.ssid,
                    location=issue.location,
                    issue_type=issue.issue_type,
                    description=issue.description,
                    cluster_key=issue.cluster_key,
                    status=STATUS_NOT_RESOLVED,
                )
            )
            existing_keys.add(complaint_key)
            inserted += 1

        session.commit()
        return (inserted, duplicates)


def sync_complaints_from_sheet() -> dict[str, int]:
    issues = fetch_issues()
    return sync_complaints(issues)


def sync_complaints(issues: list[Issue]) -> dict[str, int]:
    inserted, duplicates = _insert_new_complaints(issues)
    total_rows = len(issues)
    logger.info(
        "Complaint sync complete. total_rows=%s inserted=%s duplicates=%s",
        total_rows,
        inserted,
        duplicates,
    )
    return {
        "sheet_rows": total_rows,
        "inserted": inserted,
        "duplicates": duplicates,
    }
