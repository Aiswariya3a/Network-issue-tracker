import csv
import io
import logging
import re
from typing import Any

import requests

from app.core.config import settings
from app.models.issue import Issue
from app.utils.location_parser import parse_location

CSV_TIMEOUT_SECONDS = 15
logger = logging.getLogger(__name__)
EMAIL_MARKDOWN_PATTERN = re.compile(r"^\[(?P<text>.+?)\]\(mailto:(?P<email>.+?)\)$")


class CSVFetchError(Exception):
    pass


def _is_empty_row(row: dict[str, Any]) -> bool:
    return not any(str(value).strip() for value in row.values() if value is not None)


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_row(row: dict[str, Any]) -> dict[str, str]:
    clean: dict[str, str] = {}
    for key, value in row.items():
        clean_key = _clean(key)
        clean_value = _clean(value)
        if clean_key:
            clean[clean_key] = clean_value
    return clean


def _normalize_email(raw_email: str) -> str:
    value = raw_email.strip()
    if not value:
        return ""
    match = EMAIL_MARKDOWN_PATTERN.match(value)
    if match:
        return match.group("email").strip()
    return value


def _fetch_csv_text() -> str:
    if not settings.google_sheet_csv_url:
        raise CSVFetchError("GOOGLE_SHEET_CSV_URL is missing. Set it in your environment or .env file.")
    if "export?format=csv" not in settings.google_sheet_csv_url:
        logger.warning(
            "CSV URL may be invalid for direct export. Expected .../export?format=csv, got: %s",
            settings.google_sheet_csv_url,
        )

    try:
        logger.info("Fetching sheet CSV from URL: %s", settings.google_sheet_csv_url)
        response = requests.get(settings.google_sheet_csv_url, timeout=CSV_TIMEOUT_SECONDS)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        logger.info("CSV fetch succeeded with status=%s content_type=%s", response.status_code, content_type)
        return response.text
    except requests.RequestException as exc:
        raise CSVFetchError(f"Failed to fetch CSV data: {exc}") from exc


def fetch_issues() -> list[Issue]:
    csv_text = _fetch_csv_text()
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        logger.warning("CSV parsing found no headers. Returning empty issues list.")
        return []
    cleaned_headers = [_clean(header) for header in reader.fieldnames if header is not None]
    logger.info("Cleaned CSV headers: %s", cleaned_headers)

    issues: list[Issue] = []
    debug_rows_logged = 0
    for row_index, row in enumerate(reader, start=2):
        if _is_empty_row(row):
            continue

        try:
            clean_row = _clean_row(row)
            timestamp = clean_row.get("Timestamp", "")
            email = _normalize_email(clean_row.get("Email Address", ""))
            location = clean_row.get("Classroom / Location", "")
            issue_type = clean_row.get("Type of Issue", "")
            description = clean_row.get("Additional Details (Optional)", "")
            cluster_key = clean_row.get("Cluster Key", "")

            if location:
                location_data = parse_location(location)
            else:
                location_data = {"floor": "", "room": "", "ssid": ""}

            issues.append(
                Issue(
                    row_index=row_index,
                    timestamp=timestamp,
                    email=email,
                    floor=location_data["floor"],
                    room=location_data["room"],
                    ssid=location_data["ssid"],
                    location=location,
                    issue_type=issue_type,
                    description=description,
                    cluster_key=cluster_key,
                    status="Not Resolved",
                )
            )
            if debug_rows_logged < 3:
                print(clean_row.keys())
                logger.info("Clean row keys => %s", list(clean_row.keys()))
                logger.info("Parsed row %s => %s", debug_rows_logged + 1, issues[-1].model_dump())
                debug_rows_logged += 1
        except Exception:
            logger.exception("Skipping malformed CSV row at row_index=%s: %s", row_index, row)
            # Bad or unexpected row format should not break the endpoint.
            continue

    logger.info("Total parsed issue rows from CSV: %s", len(issues))
    return issues
