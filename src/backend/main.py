"""Точка входа FastAPI-приложения."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.backend.api.v1.translation import router as translation_router
from src.backend.api.v1.translation import set_translation_service
from src.backend.services.llm_client import create_llm_client
from src.backend.config import settings
from src.backend.services.glossary_service import GlossaryService
from src.backend.services.translation_service import TranslationService

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Инициализация и освобождение ресурсов приложения."""
    logger.info("Запуск приложения (environment=%s, llm_backend=%s)", settings.environment, settings.llm_backend)

    # Глоссарий
    glossary = GlossaryService(settings.glossary_path)
    logger.info("Глоссарий загружен: %d терминов", len(glossary.terms))

    # LLM-клиент
    llm = create_llm_client(
        backend=settings.llm_backend,
        model_path=settings.local_model_path,
        base_url=settings.litellm_base_url,
        api_key=settings.litellm_api_key,
        target_model=settings.target_model_name,
    )

    # Сервис перевода
    service = TranslationService(glossary=glossary, llm=llm)
    set_translation_service(service)

    logger.info("Приложение готово к обработке запросов.")
    yield
    logger.info("Приложение завершает работу.")


app = FastAPI(
    title="PRISM-LLM Translator API",
    description="API для перевода новостей ЕТП с внедрением корпоративного глоссария.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}


app.include_router(translation_router)
