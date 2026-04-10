from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from database.models import UserSessionLinkDB
from config import BASE_URL, DEFAULT_LINK_EXPIRY_HOURS


def generate_user_link(discovery_session_id: str, user_name: str,
                       user_role: str = "", user_department: str = "",
                       expiry_hours: int = DEFAULT_LINK_EXPIRY_HOURS) -> dict:
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=expiry_hours)).isoformat()
    link = UserSessionLinkDB.create(
        discovery_session_id=discovery_session_id,
        user_name=user_name,
        user_role=user_role,
        user_department=user_department,
        expires_at=expires_at,
    )
    link["url"] = f"{BASE_URL}?page=chat&token={link['token']}"
    return link


def validate_token(token: str) -> tuple[dict | None, str | None]:
    """Returns (link, error_message). If link is valid, error is None."""
    link = UserSessionLinkDB.get_by_token(token)
    if not link:
        return None, "Invalid session link."

    if link["status"] == "completed":
        return link, "completed"

    if link["status"] == "expired":
        return link, "expired"

    if link["expires_at"] and datetime.fromisoformat(link["expires_at"]) < datetime.now(timezone.utc):
        UserSessionLinkDB.update_status(link["id"], "expired")
        link["status"] = "expired"
        return link, "expired"

    return link, None
