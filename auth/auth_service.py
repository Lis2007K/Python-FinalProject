
from typing import Tuple, Optional
from database.db import create_user as db_create_user, verify_user as db_verify_user, get_user_by_username
from .auth_utils import validate_username_password
from database.models import User


def register_user(username: str, password: str) -> Tuple[bool, str]:

    ok, msg = validate_username_password(username, password)
    if not ok:
        return False, msg

    return db_create_user(username.strip(), password)


def login_user(username: str, password: str) -> Tuple[bool, Optional[User]]:

    if not username or not password:
        return False, None
    return db_verify_user(username.strip(), password)


def current_user_safe(user: Optional[User]) -> dict:

    if not user:
        return {}
    return {"id": user.id, "username": user.username, "created_at": user.created_at}
