from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
import secrets
import hashlib

from datetime import datetime, timezone
from typing import Optional

from fastapi import Cookie, HTTPException, Request
from database import get_connection
from psycopg.rows import dict_row
import os


ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False
    
def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_current_admin(
    session_token: Optional[str] = Cookie(default=None)
):
    if session_token is None:
        raise HTTPException(
            status_code=401,
            detail="ログインが必要です"
        )

    token_hash = hash_session_token(session_token)

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT admin_users.id, admin_users.email
                FROM admin_sessions
                JOIN admin_users
                    ON admin_sessions.admin_id = admin_users.id
                WHERE admin_sessions.token_hash = %s
                    AND admin_sessions.expires_at > %s
                """,
                (token_hash, datetime.now(timezone.utc))
            )

            admin = cursor.fetchone()

    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="ログインが必要です"
        )

    return admin



def verify_request_origin(request: Request):
    origin = request.headers.get("origin")
    app_env = os.getenv("APP_ENV", "development")

    if app_env == "production":
        allowed_origins = {
            "https://hotel-customer-management.onrender.com",
        }
    elif app_env == "staging":
        allowed_origins = {
            "https://hotel-customer-management-staging.onrender.com",
            "http://localhost:5173",
            "http://localhost:8080",  # Nginxで配信するローカルテスト用
            "http://cpjt84zuer2u8yuqx6ki3emy.162.43.5.194.sslip.io/", #Coolify frontend staging
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        }
    else:
        allowed_origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        }
        

    if origin not in allowed_origins:
        raise HTTPException(
            status_code=403,
            detail="許可されていない送信元です"
        )