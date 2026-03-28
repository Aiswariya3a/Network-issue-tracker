import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.models.issue import Issue
from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED, UpdateStatusRequest
from app.services.complaint_sync import sync_complaints_from_sheet
from app.services.dashboard import get_dashboard_data
from app.services.issues import ALLOWED_TRANSITIONS, get_all_issues, update_issue_status
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


@router.get("/status-workflow")
def get_status_workflow() -> dict:
    return {
        "default_status": STATUS_NOT_RESOLVED,
        "allowed_statuses": [STATUS_NOT_RESOLVED, STATUS_ACKNOWLEDGED, STATUS_RESOLVED],
        "allowed_transitions": {
            status: sorted(next_states) for status, next_states in ALLOWED_TRANSITIONS.items()
        },
        "validation_rules": {
            STATUS_NOT_RESOLVED: {
                "ict_member_name_required": True,
                "resolution_remark_required": False,
            },
            STATUS_ACKNOWLEDGED: {
                "ict_member_name_required": True,
                "resolution_remark_required": True,
            },
            STATUS_RESOLVED: {
                "ict_member_name_required": True,
                "resolution_remark_required": False,
            },
        },
    }


@router.post("/sync-complaints")
def post_sync_complaints(_: dict = Depends(get_current_user)) -> dict[str, int | str]:
    try:
        summary = sync_complaints_from_sheet()
        return {
            **summary,
            "message": "Complaint sync completed.",
        }
    except CSVFetchError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to sync complaints: {exc}") from exc


def _update_status_handler(
    row_index: int,
    payload: UpdateStatusRequest,
    current_user: dict,
) -> dict[str, str | int]:
    try:
        update_issue_status(
            row_index=row_index,
            status=payload.status,
            ict_member_name=payload.ict_member_name,
            resolution_remark=payload.resolution_remark,
        )
        return {
            "row_index": row_index,
            "status": payload.status,
            "ict_member_name": payload.ict_member_name or "",
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


@router.put("/issues/{row_index}/status")
def put_issue_status(
    row_index: int,
    payload: UpdateStatusRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, str | int]:
    return _update_status_handler(row_index=row_index, payload=payload, current_user=current_user)


@router.put("/update-status/{row_index}")
def put_update_status_backward_compat(
    row_index: int,
    payload: UpdateStatusRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, str | int]:
    return _update_status_handler(row_index=row_index, payload=payload, current_user=current_user)
