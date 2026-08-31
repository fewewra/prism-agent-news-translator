"""Сервис-оркестратор перевода: глоссарий → промпт → LLM."""

from __future__ import annotations

import logging
import time
from typing import List

from src.backend.api.schemas import (
    GlossaryTermApplied,
    TranslationMeta,
    TranslationRequest,
    TranslationResponse,
)
from src.backend.services.glossary_service import GlossaryService, GlossaryTerm
from src.backend.services.llm_client import BaseLLMClient
from src.backend.services.prompt_service import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class TranslationService:
    """Оркестратор: принимает запрос, находит термины, строит промпты, вызывает LLM."""

    def __init__(
        self,
        glossary: GlossaryService,
        llm: BaseLLMClient,
    ) -> None:
        self._glossary = glossary
        self._llm = llm

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Выполнить полный цикл перевода новости (title, announce, detail_text)."""
        start_time = time.perf_counter()

        # 1. Собираем весь текст новости для единого поиска терминов
        full_text_parts = [
            text for text in (request.title, request.announce, request.detail_text) if text
        ]
        full_text = "\n".join(full_text_parts)

        # 2. Фильтруем через pymorphy3 только те термины из request.glossary, которые физически есть в тексте
        matched_terms: List[GlossaryTerm] = self._glossary.match_terms(
            full_text, glossary_input=request.glossary, limit=10
        )

        # 4. Выполняем перевод каждого присутствующего текстового поля
        translated_title: str | None = None
        if request.title:
            prompt_title = build_user_prompt(request.title, matched_terms)
            translated_title = await self._llm.generate(SYSTEM_PROMPT, prompt_title)

        translated_announce: str | None = None
        if request.announce:
            prompt_announce = build_user_prompt(request.announce, matched_terms)
            translated_announce = await self._llm.generate(SYSTEM_PROMPT, prompt_announce)

        translated_detail_text: str | None = None
        if request.detail_text:
            prompt_detail = build_user_prompt(request.detail_text, matched_terms)
            translated_detail_text = await self._llm.generate(
                SYSTEM_PROMPT, prompt_detail
            )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "Перевод новости news_id=%d выполнен за %d ms, примененено %d терминов",
            request.news_id,
            elapsed_ms,
            len(matched_terms),
        )

        return TranslationResponse(
            news_id=request.news_id,
            translated_title=translated_title,
            translated_announce=translated_announce,
            translated_detail_text=translated_detail_text,
            meta=TranslationMeta(
                model_used=self._llm.model_name(),
                processing_time_ms=elapsed_ms,
                terms_applied=[
                    GlossaryTermApplied(
                        term_id=t.term_id,
                        ru_term=t.ru_term,
                        en_preferred=t.en_preferred,
                    )
                    for t in matched_terms
                ],
            ),
        )
