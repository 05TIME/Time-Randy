"""Authentication and business authorization for the TIMEŒ API.

User authentication is performed against Supabase Auth using the caller's
Bearer access token. Server-side database access continues to use the
service-role credential, which is never returned to the client.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Response, request


def _supabase_auth_url() -> str:
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    if not url:
        raise RuntimeError("SUPABASE_URL is required")
    return f"{url}/auth/v1/user"


def _publishable_key() -> str:
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not key:
        raise RuntimeError("SUPABASE_PUBLISHABLE_KEY is required")
    return key


def authenticate_request() -> str:
    """Verify the caller's Supabase access token and return the user id."""
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise PermissionError("missing bearer token")

    req = Request(
        _supabase_auth_url(),
        headers={
            "apikey": _publishable_key(),
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise PermissionError("invalid or expired access token") from exc
        raise RuntimeError(f"Supabase Auth returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Supabase Auth could not be reached") from exc
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError("Supabase Auth returned invalid JSON") from exc

    user_id = payload.get("id")
    if not user_id:
        raise PermissionError("authenticated user id missing")
    return str(user_id)


def unauthorized_response(message: str = "authentication required") -> Response:
    response = Response(message, status=401)
    response.headers["WWW-Authenticate"] = 'Bearer realm="TIMEŒ"'
    return response


def authorize_business(client, user_id: str, business_id: str) -> bool:
    """Allow business owners or members to access a business's data."""
    owner = (
        client.table("businesses")
        .select("id")
        .eq("id", business_id)
        .eq("owner_id", user_id)
        .limit(1)
        .execute()
        .data
    )
    if owner:
        return True

    membership = (
        client.table("memberships")
        .select("id")
        .eq("business_id", business_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
    )
    return bool(membership)
