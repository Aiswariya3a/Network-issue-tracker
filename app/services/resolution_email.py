import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings
from app.models.issue import Issue
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_RESOLVED

logger = logging.getLogger(__name__)


def send_status_email(
    issue: Issue,
    status: str,
    ict_member_name: str,
    resolution_remark: str | None = None,
) -> None:
    recipient = issue.email.strip()
    if not recipient:
        logger.warning("Status email skipped for row=%s: recipient email missing.", issue.row_index)
        return

    if not settings.email_sender or not settings.email_password:
        logger.warning("Status email skipped for row=%s: sender config missing.", issue.row_index)
        return

    if status == STATUS_RESOLVED:
        subject = "Network Issue Resolved"
        opening = "Your reported network issue has been marked as RESOLVED."
        remark_value = resolution_remark.strip() if resolution_remark else "No additional resolution remark provided."
    elif status == STATUS_ACKNOWLEDGED:
        subject = "Network Issue Acknowledged"
        opening = "Your reported network issue has been ACKNOWLEDGED by ICT and is being worked on."
        remark_value = resolution_remark.strip() if resolution_remark else "No remark provided."
    else:
        logger.info("Status email skipped for row=%s: status=%s does not require email.", issue.row_index, status)
        return

    body = (
        "Hello,\n\n"
        f"{opening}\n\n"
        f"Issue Type: {issue.issue_type or 'N/A'}\n"
        f"Location: {issue.location or 'N/A'}\n"
        f"Description: {issue.description or 'N/A'}\n"
        f"ICT Member: {ict_member_name}\n"
        f"Resolution Remark: {remark_value}\n\n"
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
        logger.info("Status email sent to %s for row=%s status=%s", recipient, issue.row_index, status)
    except Exception as exc:
        logger.exception("Failed to send status email for row=%s: %s", issue.row_index, exc)
