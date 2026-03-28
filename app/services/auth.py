from app.core.auth import create_access_token, hash_password, verify_password
from app.db.user_repo import create_user_if_missing, get_user_by_username

DEFAULT_USERNAME = "ict_admin"
DEFAULT_PASSWORD = "admin123"
DEFAULT_ROLE = "ICT"


def seed_default_user() -> None:
    create_user_if_missing(
        username=DEFAULT_USERNAME,
        password_hash=hash_password(DEFAULT_PASSWORD),
        role=DEFAULT_ROLE,
    )


def login_user(username: str, password: str) -> str:
    user = get_user_by_username(username)
    if user is None:
        raise ValueError("Invalid username or password.")

    if not verify_password(password, str(user["password_hash"])):
        raise ValueError("Invalid username or password.")

    return create_access_token(
        {
            "sub": str(user["username"]),
            "role": str(user["role"]),
        }
    )
