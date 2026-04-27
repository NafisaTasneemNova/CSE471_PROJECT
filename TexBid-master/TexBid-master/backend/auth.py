"""
auth.py — JWT authentication helpers for TexBid.

Provides:
  - JWT token creation (access + refresh)
  - Token verification
  - FastAPI dependencies for role-based access control
  - Dual-mode auth: accepts both JWT (Bearer) and legacy session cookie
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Cookie, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# ── Configuration ────────────────────────────────────────────────────────────
# Override via environment variable in production.
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "texbid-jwt-secret-change-in-production")
JWT_ALGORITHM:  str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES:  int = 60 * 24        # 24 hours
REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30   # 30 days

# Roles
ROLE_BUYER    = "BUYER"
ROLE_SUPPLIER = "SUPPLIER"
ROLE_ADMIN    = "ADMIN"

# Optional bearer scheme (auto_error=False so we can fall back to session)
_bearer_scheme = HTTPBearer(auto_error=False)


# ── Token creation ────────────────────────────────────────────────────────────

def create_access_token(user_id: str, email: str, role: str, is_admin: bool,
                        company_id: Optional[str] = None,
                        expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Payload claims:
      sub       — user ID
      email     — user email
      role      — BUYER | SUPPLIER | ADMIN
      is_admin  — boolean
      company_id — linked company ID (may be None)
      type      — "access"
      exp       — expiry timestamp
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub":        user_id,
        "email":      email,
        "role":       role,
        "is_admin":   is_admin,
        "company_id": company_id,
        "type":       "access",
        "exp":        expire,
        "iat":        datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token (contains only sub + type)."""
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "exp":  expire,
        "iat":  datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    Raises HTTPException 401 on any failure.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Internal helpers ──────────────────────────────────────────────────────────

async def _user_from_jwt(token: str) -> Optional[dict]:
    """Resolve a JWT token to a full user dict from the database."""
    from database import db
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id or db is None:
            return None
        user = await db["users"].find_one({"id": user_id})
        return user
    except HTTPException:
        return None


async def _user_from_session(session_token: Optional[str]) -> Optional[dict]:
    """Resolve a legacy session cookie to a user dict."""
    if not session_token:
        return None
    from main import get_user_from_session   # avoid circular at module level
    from database import db
    user_id = get_user_from_session(session_token)
    if not user_id or db is None:
        return None
    return await db["users"].find_one({"id": user_id})


# ── FastAPI dependencies ──────────────────────────────────────────────────────

async def get_current_user_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    session: Optional[str] = Cookie(None),
) -> Optional[dict]:
    """
    Dual-mode dependency: accepts JWT Bearer token OR legacy session cookie.
    Returns the user dict, or None if unauthenticated.
    """
    # 1. Try JWT Bearer first
    if credentials and credentials.scheme.lower() == "bearer":
        user = await _user_from_jwt(credentials.credentials)
        if user:
            return user

    # 2. Fall back to session cookie (backward compat)
    if session:
        user = await _user_from_session(session)
        if user:
            return user

    return None


async def require_login_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    session: Optional[str] = Cookie(None),
) -> dict:
    """Require authentication (JWT or session). Raises 401 if not authenticated."""
    user = await get_current_user_jwt(credentials, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token or log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_role(required_role: str, user: dict) -> dict:
    """
    Verify the user's company has the required role.
    Raises 403 if the role doesn't match.
    """
    from database import db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    company = await db["companies"].find_one({"id": user.get("company_id")})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.get("role") != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {required_role}. Your role: {company.get('role')}",
        )
    return user


# ── Role-specific dependencies ────────────────────────────────────────────────

async def require_buyer(user: dict = Depends(require_login_jwt)) -> dict:
    """Require authenticated BUYER role."""
    return await require_role(ROLE_BUYER, user)


async def require_supplier(user: dict = Depends(require_login_jwt)) -> dict:
    """Require authenticated SUPPLIER role."""
    return await require_role(ROLE_SUPPLIER, user)


async def require_admin_jwt(user: dict = Depends(require_login_jwt)) -> dict:
    """Require admin flag on the user."""
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# ── Token refresh endpoint helper ─────────────────────────────────────────────

async def refresh_access_token(refresh_token: str) -> str:
    """
    Validate a refresh token and issue a new access token.
    Raises 401 on invalid/expired refresh token.
    """
    from database import db
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {exc}",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload.get("sub")
    if not user_id or db is None:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = await db["users"].find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    company = await db["companies"].find_one({"id": user.get("company_id")})
    role = company.get("role", "BUYER") if company else "BUYER"

    return create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=role,
        is_admin=user.get("is_admin", False),
        company_id=user.get("company_id"),
    )
