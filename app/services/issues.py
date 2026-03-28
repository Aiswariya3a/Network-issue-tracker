from app.db.status_repo import ALLOWED_STATUSES, get_status, update_or_insert_status
from app.models.issue import Issue
from app.services.resolution_email import send_resolution_email
from app.services.sheets import fetch_issues


def get_all_issues() -> list[Issue]:
    issues = fetch_issues()
    for issue in issues:
        issue.status = get_status(issue.row_index)
    return issues


def update_issue_status(row_index: int, status: str, resolution_note: str | None = None) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Status must be one of: Resolved, Not Resolved.")
    if row_index < 2:
        raise LookupError("Invalid row_index. Row index must be >= 2.")

    issues = fetch_issues()
    issue = next((item for item in issues if item.row_index == row_index), None)
    if issue is None:
        raise LookupError(f"Issue row {row_index} was not found in the current sheet data.")

    existing_status = get_status(row_index=row_index)
    if existing_status != status:
        update_or_insert_status(row_index=row_index, status=status)

    if existing_status != "Resolved" and status == "Resolved":
        send_resolution_email(issue=issue, resolution_note=resolution_note)
