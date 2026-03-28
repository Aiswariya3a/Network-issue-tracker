import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.services.retention import cleanup_old_complaints
from app.services.report_email import send_daily_report

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler

    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(
        timezone=settings.scheduler_timezone,
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            # Allow delayed execution after brief downtime/restart windows.
            "misfire_grace_time": 60 * 60,
        },
    )
    _scheduler.add_listener(_job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    if settings.report_test_interval_minutes > 0:
        _scheduler.add_job(
            send_daily_report,
            trigger=IntervalTrigger(minutes=settings.report_test_interval_minutes, timezone=settings.scheduler_timezone),
            id="daily_network_report",
            replace_existing=True,
        )
        logger.info(
            "Report scheduler started in test mode (every %s minute(s)).",
            settings.report_test_interval_minutes,
        )
    else:
        _scheduler.add_job(
            send_daily_report,
            trigger=CronTrigger(
                hour=settings.report_hour,
                minute=settings.report_minute,
                timezone=settings.scheduler_timezone,
            ),
            id="daily_network_report",
            replace_existing=True,
        )
        logger.info(
            "Report scheduler started (daily at %02d:%02d %s).",
            settings.report_hour,
            settings.report_minute,
            settings.scheduler_timezone,
        )

    _scheduler.add_job(
        _run_retention_cleanup,
        trigger=CronTrigger(
            hour=settings.retention_cleanup_hour,
            minute=settings.retention_cleanup_minute,
            timezone=settings.scheduler_timezone,
        ),
        id="daily_retention_cleanup",
        replace_existing=True,
    )
    logger.info(
        "Retention cleanup scheduler started (daily at %02d:%02d %s, retention=%s days, archive=%s).",
        settings.retention_cleanup_hour,
        settings.retention_cleanup_minute,
        settings.scheduler_timezone,
        settings.retention_days,
        settings.archive_before_delete,
    )

    _scheduler.start()
    _log_job_schedule("daily_network_report")
    _log_job_schedule("daily_retention_cleanup")


def stop_scheduler() -> None:
    global _scheduler

    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Report scheduler stopped.")

    _scheduler = None


def _run_retention_cleanup() -> None:
    try:
        result = cleanup_old_complaints(
            retention_days=settings.retention_days,
            archive_before_delete=settings.archive_before_delete,
        )
        logger.info("Retention cleanup job result: %s", result)
    except Exception:
        logger.exception("Retention cleanup job failed.")


def _job_listener(event: JobExecutionEvent) -> None:
    if event.exception:
        logger.error(
            "Scheduled job failed. job_id=%s exception=%s traceback=%s",
            event.job_id,
            event.exception,
            event.traceback,
        )
    else:
        logger.info("Scheduled job executed successfully. job_id=%s", event.job_id)


def _log_job_schedule(job_id: str) -> None:
    if not _scheduler:
        return
    job = _scheduler.get_job(job_id)
    if not job:
        logger.warning("Scheduler job not found: %s", job_id)
        return
    logger.info(
        "Scheduler job registered. job_id=%s next_run_time=%s trigger=%s",
        job.id,
        job.next_run_time,
        job.trigger,
    )
