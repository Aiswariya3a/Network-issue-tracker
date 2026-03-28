from fastapi import APIRouter, HTTPException, status

from app.models.auth import LoginRequest, TokenResponse
from app.services.auth import login_user

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    try:
        token = login_user(username=payload.username, password=payload.password)
        return TokenResponse(access_token=token, token_type="bearer")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
