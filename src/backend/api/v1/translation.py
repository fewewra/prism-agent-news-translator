"""Роутер эндпоинта перевода."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.backend.dependencies import verify_api_key
from src.backend.api.schemas import TranslationRequest, TranslationResponse

router = APIRouter(prefix="/api/v1", tags=["translation"])

# Будет установлен при старте приложения
_translation_service = None


def set_translation_service(service) -> None:
    global _translation_service
    _translation_service = service


@router.post("/translate", response_model=TranslationResponse)
async def translate(
    request: TranslationRequest,
    _api_key: str = Depends(verify_api_key),
) -> TranslationResponse:
    """Перевод текста новости RU→EN с опциональным глоссарием в запросе."""
    return await _translation_service.translate(request)

