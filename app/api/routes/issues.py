import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.models.issue import Issue
from app.models.status import UpdateStatusRequest
from app.services.dashboard import get_dashboard_data
from app.services.issues import get_all_issues, update_issue_status
from app.services.sheets import CSVFetchError

router = APIRouter(tags=["issues"])
logger = logging.getLogger(__name__)


@router.get("/issues", response_model=list[Issue])
def get_issues() -> list[Issue]:
    try:
        return get_all_issues()
    except CSVFetchError as exc:
        logger.exception("GET /issues failed due to CSV fetch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("GET /issues failed unexpectedly: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to process CSV data: {exc}") from exc


@router.get("/dashboard")
def get_dashboard() -> dict:
    try:
        return get_dashboard_data()
    except CSVFetchError as exc:
        logger.exception("GET /dashboard failed due to CSV fetch error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("GET /dashboard failed unexpectedly: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to build dashboard data: {exc}") from exc


@router.put("/update-status/{row_index}")
def put_update_status(
    row_index: int,
    payload: UpdateStatusRequest,
    _: dict = Depends(get_current_user),
) -> dict[str, str | int]:
    try:
        update_issue_status(
            row_index=row_index,
            status=payload.status,
            resolution_note=payload.resolution_note,
        )
        return {
            "row_index": row_index,
            "status": payload.status,
            "message": "Status updated successfully.",
        }
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CSVFetchError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update issue status: {exc}") from exc
