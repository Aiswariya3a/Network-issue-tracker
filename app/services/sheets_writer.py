import logging
import re

import gspread

from app.core.config import settings

logger = logging.getLogger(__name__)
SHEET_ID_PATTERN = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


def _resolve_sheet_id() -> str:
    if settings.google_sheet_id:
        return settings.google_sheet_id

    match = SHEET_ID_PATTERN.search(settings.google_sheet_csv_url)
    if match:
        return match.group(1)

    return ""


def update_sheet_status(row_index: int, status: str) -> None:
    if not settings.google_service_account_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is required to update status in Google Sheet.")
    sheet_id = _resolve_sheet_id()
    if not sheet_id:
        raise RuntimeError("GOOGLE_SHEET_ID could not be resolved. Set GOOGLE_SHEET_ID explicitly.")

    client = gspread.service_account(filename=settings.google_service_account_file)
    worksheet = client.open_by_key(sheet_id).worksheet(settings.google_worksheet_name)

    header = [str(cell).strip() for cell in worksheet.row_values(1)]
    try:
        status_col_idx = header.index(settings.google_status_column_name) + 1
    except ValueError as exc:
        raise RuntimeError(
            f"Status column '{settings.google_status_column_name}' not found in worksheet header."
        ) from exc

    worksheet.update_cell(row_index, status_col_idx, status)
    logger.info(
        "Updated Google Sheet status at row=%s col=%s (%s) to '%s'.",
        row_index,
        status_col_idx,
        settings.google_status_column_name,
        status,
    )
