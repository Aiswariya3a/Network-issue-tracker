from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.db.user_repo import get_user_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
ALLOWED_COORDINATOR_ROLES = {"ICT", "Infra"}


def hash_password(password: str) -> str:
    if len(password.encode("utf-8"))>72:
        raise ValueError("Password too long(max 72 bytes for bcrypt)")
    return pwd_context.hash(password)
    
 


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    user = get_user_by_username(str(username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    role = str(user["role"])
    if role not in ALLOWED_COORDINATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permission.")

    return user
