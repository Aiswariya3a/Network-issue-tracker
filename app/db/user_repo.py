from typing import Any

from sqlalchemy import select

from app.db.database import get_session
from app.db.orm_models import User


def get_user_by_username(username: str) -> dict[str, Any] | None:
    with get_session() as session:
        user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()

    if user is None:
        return None

    return {
        "id": int(user.id),
        "username": str(user.username),
        "password_hash": str(user.password_hash),
        "role": str(user.role),
    }


def create_user_if_missing(username: str, password_hash: str, role: str) -> None:
    with get_session() as session:
        existing = session.execute(select(User.id).where(User.username == username)).scalar_one_or_none()
        if existing is not None:
            return

        session.add(User(username=username, password_hash=password_hash, role=role))
        session.commit()
