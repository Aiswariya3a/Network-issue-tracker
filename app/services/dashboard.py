from collections import Counter
import logging
from typing import Any

from app.models.issue import Issue
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED
from app.services.issues import get_all_issues

logger = logging.getLogger(__name__)


def get_issue_type_counts(issues: list[Issue]) -> dict[str, int]:
    counter = Counter(issue.issue_type.strip() for issue in issues if issue.issue_type.strip())
    return dict(counter)


def get_status_counts(issues: list[Issue]) -> dict[str, int]:
    counter = Counter(issue.status.strip() for issue in issues if issue.status.strip())
    return {
        STATUS_NOT_RESOLVED: counter.get(STATUS_NOT_RESOLVED, 0),
        STATUS_ACKNOWLEDGED: counter.get(STATUS_ACKNOWLEDGED, 0),
        STATUS_RESOLVED: counter.get(STATUS_RESOLVED, 0),
    }


def get_acknowledgement_metrics(status_summary: dict[str, int]) -> dict[str, int | float]:
    total = (
        status_summary.get(STATUS_NOT_RESOLVED, 0)
        + status_summary.get(STATUS_ACKNOWLEDGED, 0)
        + status_summary.get(STATUS_RESOLVED, 0)
    )
    acknowledged = status_summary.get(STATUS_ACKNOWLEDGED, 0)
    resolved = status_summary.get(STATUS_RESOLVED, 0)
    pending_unacknowledged = status_summary.get(STATUS_NOT_RESOLVED, 0)
    actioned = acknowledged + resolved
    actioned_rate = round((actioned / total) * 100, 2) if total else 0.0
    return {
        "total_issues": total,
        "actioned_issues": actioned,
        "pending_unacknowledged": pending_unacknowledged,
        "actioned_rate_percent": actioned_rate,
    }


def get_location_counts(issues: list[Issue]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for issue in issues:
        floor = issue.floor.strip()
        room = issue.room.strip()
        if not floor or not room:
            continue
        counter[f"{floor}-{room}"] += 1
    return dict(counter)


def get_cluster_counts(issues: list[Issue]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for issue in issues:
        cluster_key = issue.cluster_key.strip()
        if not cluster_key:
            continue
        counter[cluster_key] += 1

    return [{"cluster": cluster, "count": count} for cluster, count in counter.most_common()]


def build_dashboard_response(issues: list[Issue]) -> dict[str, Any]:
    status_summary = get_status_counts(issues)
    return {
        "issue_types": get_issue_type_counts(issues),
        "status_summary": status_summary,
        "acknowledgement_metrics": get_acknowledgement_metrics(status_summary),
        "location_stats": get_location_counts(issues),
        "clusters": get_cluster_counts(issues),
    }


def get_dashboard_data() -> dict[str, Any]:
    issues = get_all_issues()
    logger.info("Building dashboard from %s issues.", len(issues))
    if not issues:
        return {
            "issue_types": {},
            "status_summary": {
                STATUS_NOT_RESOLVED: 0,
                STATUS_ACKNOWLEDGED: 0,
                STATUS_RESOLVED: 0,
            },
            "acknowledgement_metrics": {
                "total_issues": 0,
                "actioned_issues": 0,
                "pending_unacknowledged": 0,
                "actioned_rate_percent": 0.0,
            },
            "location_stats": {},
            "clusters": [],
        }
    return build_dashboard_response(issues)
