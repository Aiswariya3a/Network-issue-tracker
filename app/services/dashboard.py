from collections import Counter
import logging
from typing import Any

from app.models.issue import Issue
from app.services.issues import get_all_issues

logger = logging.getLogger(__name__)


def get_issue_type_counts(issues: list[Issue]) -> dict[str, int]:
    counter = Counter(issue.issue_type.strip() for issue in issues if issue.issue_type.strip())
    return dict(counter)


def get_status_counts(issues: list[Issue]) -> dict[str, int]:
    counter = Counter(issue.status.strip() for issue in issues if issue.status.strip())
    return {
        "Resolved": counter.get("Resolved", 0),
        "Not Resolved": counter.get("Not Resolved", 0),
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
    return {
        "issue_types": get_issue_type_counts(issues),
        "status_summary": get_status_counts(issues),
        "location_stats": get_location_counts(issues),
        "clusters": get_cluster_counts(issues),
    }


def get_dashboard_data() -> dict[str, Any]:
    issues = get_all_issues()
    logger.info("Building dashboard from %s issues.", len(issues))
    if not issues:
        return {
            "issue_types": {},
            "status_summary": {"Open": 0, "Resolved": 0, "Not Resolved": 0},
            "location_stats": {},
            "clusters": [],
        }
    return build_dashboard_response(issues)
