import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings
from app.models.issue import Issue

logger = logging.getLogger(__name__)


def send_resolution_email(issue: Issue, resolution_note: str | None = None) -> None:
    recipient = issue.email.strip()
    if not recipient:
        logger.warning("Resolution email skipped for row=%s: recipient email missing.", issue.row_index)
        return

    if not settings.email_sender or not settings.email_password:
        logger.warning("Resolution email skipped for row=%s: sender config missing.", issue.row_index)
        return

    subject = "Network Issue Resolved"
    note_block = resolution_note.strip() if resolution_note else "No additional notes were provided."
    body = (
        "Hello,\n\n"
        "Your reported network issue has been marked as resolved.\n\n"
        f"Issue Type: {issue.issue_type or 'N/A'}\n"
        f"Location: {issue.location or 'N/A'}\n"
        f"Description: {issue.description or 'N/A'}\n"
        f"Resolution Note: {note_block}\n\n"
        "If the issue still persists, please submit a new report.\n\n"
        "Regards,\n"
        "ICT Support Team"
    )

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = settings.email_sender
    message["To"] = recipient

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.email_sender, settings.email_password)
            server.sendmail(settings.email_sender, recipient, message.as_string())
        logger.info("Resolution email sent to %s for row=%s", recipient, issue.row_index)
    except Exception as exc:
        logger.exception("Failed to send resolution email for row=%s: %s", issue.row_index, exc)
