import csv
import logging
import smtplib
from collections import Counter
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.db.database import get_session
from app.db.orm_models import Complaint
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED
from app.services.dashboard import get_dashboard_data
from app.services.issues import get_all_issues
from app.services.report_builder import generate_pdf_report, generate_pie_chart
from sqlalchemy import select

logger = logging.getLogger(__name__)


def _safe_max_key(counts: dict[str, int]) -> str:
    if not counts:
        return "N/A"
    return max(counts, key=counts.get)


def _build_report_summary(dashboard: dict[str, Any]) -> dict[str, Any]:
    issue_types = dashboard.get("issue_types", {})
    location_stats = dashboard.get("location_stats", {})
    status_summary = dashboard.get("status_summary", {})
    clusters = dashboard.get("clusters", [])

    total_issues = int(sum(int(v) for v in issue_types.values()))
    resolved_count = int(status_summary.get(STATUS_RESOLVED, 0))
    acknowledged_count = int(status_summary.get(STATUS_ACKNOWLEDGED, 0))
    not_resolved_count = int(status_summary.get(STATUS_NOT_RESOLVED, 0))
    resolution_rate = (resolved_count / total_issues * 100) if total_issues > 0 else 0.0

    return {
        "total_issues": total_issues,
        "resolved_count": resolved_count,
        "acknowledged_count": acknowledged_count,
        "not_resolved_count": not_resolved_count,
        "resolution_rate": resolution_rate,
        "top_issue_type": _safe_max_key(issue_types),
        "most_affected_location": _safe_max_key(location_stats),
        "issue_types": issue_types,
        "status_summary": {
            STATUS_RESOLVED: int(status_summary.get(STATUS_RESOLVED, 0)),
            STATUS_ACKNOWLEDGED: int(status_summary.get(STATUS_ACKNOWLEDGED, 0)),
            STATUS_NOT_RESOLVED: int(status_summary.get(STATUS_NOT_RESOLVED, 0)),
        },
        "clusters": clusters,
    }


def _build_report_summary_from_db() -> dict[str, Any]:
    with get_session() as session:
        complaints = session.execute(select(Complaint)).scalars().all()

    issue_type_counter: Counter[str] = Counter()
    location_counter: Counter[str] = Counter()
    status_counter: Counter[str] = Counter()
    cluster_counter: Counter[str] = Counter()

    for complaint in complaints:
        issue_type = (complaint.issue_type or "").strip()
        if issue_type:
            issue_type_counter[issue_type] += 1

        floor = (complaint.floor or "").strip()
        room = (complaint.room or "").strip()
        if floor and room:
            location_counter[f"{floor}-{room}"] += 1

        status = (complaint.status or "").strip()
        if status:
            status_counter[status] += 1

        cluster_key = (complaint.cluster_key or "").strip()
        if cluster_key:
            cluster_counter[cluster_key] += 1

    dashboard_fallback = {
        "issue_types": dict(issue_type_counter),
        "location_stats": dict(location_counter),
        "status_summary": {
            STATUS_RESOLVED: int(status_counter.get(STATUS_RESOLVED, 0)),
            STATUS_ACKNOWLEDGED: int(status_counter.get(STATUS_ACKNOWLEDGED, 0)),
            STATUS_NOT_RESOLVED: int(status_counter.get(STATUS_NOT_RESOLVED, 0)),
        },
        "clusters": [{"cluster": cluster, "count": count} for cluster, count in cluster_counter.most_common()],
    }
    return _build_report_summary(dashboard_fallback)


def _attach_file(message: MIMEMultipart, file_path: Path, mime_subtype: str = "octet-stream") -> None:
    if not file_path.exists():
        return
    with file_path.open("rb") as file_handle:
        part = MIMEBase("application", mime_subtype)
        part.set_payload(file_handle.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
    message.attach(part)


def _write_raw_csv(file_path: Path) -> None:
    issues = get_all_issues()
    headers = [
        "row_index",
        "complaint_key",
        "timestamp",
        "email",
        "floor",
        "room",
        "ssid",
        "location",
        "issue_type",
        "description",
        "cluster_key",
        "status",
    ]
    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for issue in issues:
            writer.writerow(
                [
                    issue.row_index,
                    issue.complaint_key or "",
                    issue.timestamp,
                    issue.email,
                    issue.floor,
                    issue.room,
                    issue.ssid,
                    issue.location,
                    issue.issue_type,
                    issue.description,
                    issue.cluster_key,
                    issue.status,
                ]
            )


def send_daily_report() -> None:
    if not settings.email_sender or not settings.email_password or not settings.email_receiver:
        logger.warning("Daily report skipped: email configuration is incomplete.")
        return

    try:
        logger.info(
            "Preparing daily report email. sender=%s receiver=%s smtp=%s:%s",
            settings.email_sender,
            settings.email_receiver,
            settings.smtp_host,
            settings.smtp_port,
        )
        using_fallback = False
        try:
            dashboard = get_dashboard_data()
            summary = _build_report_summary(dashboard)
        except Exception as dashboard_exc:
            using_fallback = True
            logger.exception(
                "Dashboard snapshot failed for daily report; falling back to DB summary: %s",
                dashboard_exc,
            )
            summary = _build_report_summary_from_db()

        tz = ZoneInfo(settings.scheduler_timezone)
        today = datetime.now(tz).strftime("%Y-%m-%d")
        subject = f"Daily Network Report - {today}"
        body = (
            "Please find attached the daily network report with issue analysis "
            "and resolution summary."
        )
        if using_fallback:
            body += "\n\nNote: Report was generated from database snapshot due to temporary sheet fetch issue."

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            chart_path = temp_path / "status_chart.png"
            pdf_path = temp_path / "daily_report.pdf"
            raw_csv_path = temp_path / "daily_issues_raw.csv"

            generate_pie_chart(summary["status_summary"], output_path=str(chart_path))
            generate_pdf_report(summary, chart_path=str(chart_path), output_path=str(pdf_path))

            message = MIMEMultipart()
            message["From"] = settings.email_sender
            message["To"] = settings.email_receiver
            message["Subject"] = subject
            message["Date"] = formatdate(localtime=True)
            message["Message-ID"] = make_msgid(domain=settings.email_sender.split("@")[-1])
            message.attach(MIMEText(body, "plain"))

            _attach_file(message, pdf_path, mime_subtype="pdf")

            if settings.attach_raw_csv_report:
                _write_raw_csv(raw_csv_path)
                _attach_file(message, raw_csv_path, mime_subtype="csv")

            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.email_sender, settings.email_password)
                send_result = server.sendmail(settings.email_sender, settings.email_receiver, message.as_string())
                if send_result:
                    logger.error("SMTP sendmail reported refused recipients: %s", send_result)
                else:
                    logger.info("SMTP sendmail accepted message for delivery.")

        logger.info(
            "Daily report email sent successfully to %s with message-id %s",
            settings.email_receiver,
            message["Message-ID"],
        )
    except smtplib.SMTPAuthenticationError as exc:
        logger.error(
            "SMTP authentication failed for sender=%s. "
            "Use a Gmail App Password (16 chars) with 2FA enabled. Error: %s",
            settings.email_sender,
            exc,
        )
    except Exception as exc:
        logger.exception("Failed to send daily report email: %s", exc)
