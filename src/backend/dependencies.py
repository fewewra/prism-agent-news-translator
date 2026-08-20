"""FastAPI-зависимости: M2M-авторизация через заголовок X-API-Key."""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from src.backend.config import settings


async def verify_api_key(
    x_api_key: str = Header(..., description="Статический M2M-токен авторизации"),
) -> str:
    """Проверить X-API-Key заголовок запроса."""
    if not hmac.compare_digest(x_api_key, settings.bitrix_auth_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
