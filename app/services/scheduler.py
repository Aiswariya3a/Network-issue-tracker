import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.services.report_email import send_daily_report

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler

    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)

    if settings.report_test_interval_minutes > 0:
        _scheduler.add_job(
            send_daily_report,
            trigger=IntervalTrigger(minutes=settings.report_test_interval_minutes),
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
            trigger=CronTrigger(hour=settings.report_hour, minute=settings.report_minute),
            id="daily_network_report",
            replace_existing=True,
        )
        logger.info(
            "Report scheduler started (daily at %02d:%02d %s).",
            settings.report_hour,
            settings.report_minute,
            settings.scheduler_timezone,
        )

    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler

    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Report scheduler stopped.")

    _scheduler = None
