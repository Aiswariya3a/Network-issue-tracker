from datetime import datetime, timezone

from app.db.status_repo import get_status_details, get_status_details_map, update_status
from app.models.issue import Issue
from app.models.status import (
    ALLOWED_STATUSES,
    STATUS_ACKNOWLEDGED,
    STATUS_NOT_RESOLVED,
    STATUS_RESOLVED,
)
from app.services.complaint_sync import build_complaint_key, sync_complaints
from app.services.resolution_email import send_status_email
from app.services.sheets import fetch_issues

ALLOWED_TRANSITIONS = {
    STATUS_NOT_RESOLVED: {STATUS_ACKNOWLEDGED, STATUS_RESOLVED},
    STATUS_ACKNOWLEDGED: {STATUS_RESOLVED, STATUS_NOT_RESOLVED},
    STATUS_RESOLVED: set(),
}


def get_all_issues() -> list[Issue]:
    issues = fetch_issues()
    # Persist new sheet rows first; existing complaints are never overwritten.
    sync_complaints(issues)

    complaint_keys = [build_complaint_key(issue) for issue in issues]
    details_map = get_status_details_map(complaint_keys)
    for issue in issues:
        complaint_key = build_complaint_key(issue)
        details = details_map.get(complaint_key)
        if details is None:
            issue.status = STATUS_NOT_RESOLVED
            continue

        issue.complaint_key = complaint_key
        issue.status = str(details["status"])
        issue.ict_member_name = details["ict_member_name"]
        issue.resolution_remark = details["resolution_remark"]
        issue.acknowledged_at = details["acknowledged_at"]
        issue.resolved_at = details["resolved_at"]
    return issues


def update_issue_status(
    row_index: int,
    status: str,
    ict_member_name: str | None,
    resolution_remark: str | None = None,
) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Status must be one of: NOT RESOLVED, ACKNOWLEDGED, RESOLVED.")
    if row_index < 2:
        raise LookupError("Invalid row_index. Row index must be >= 2.")

    issues = fetch_issues()
    issue = next((item for item in issues if item.row_index == row_index), None)
    if issue is None:
        raise LookupError(f"Issue row {row_index} was not found in the current sheet data.")

    complaint_key = build_complaint_key(issue)
    issue.complaint_key = complaint_key

    # Ensure complaint exists in DB before attempting status changes.
    sync_complaints(issues)

    existing = get_status_details(complaint_key=complaint_key)
    existing_status = str(existing["status"])
    if existing_status == status:
        raise ValueError(f"Issue row {row_index} is already in status '{status}'.")

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
