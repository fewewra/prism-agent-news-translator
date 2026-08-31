"""Расширенный тест устойчивости перевода и работы глоссария на 4 разнородных кейсах."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.backend.api.schemas import TranslationRequest
from src.backend.services.translation_service import TranslationService

TEST_CASES = [
    {
        "news_id": 801,
        "name": "Кейс 1: Аббревиатуры и термины в косвенных падежах (ВПУ, танкеры, морской терминал)",
        "title": "Работы на выносном причальном устройстве",
        "detail_text": "На морском терминале завершилась швартовка танкера к выносным причальным устройствам (ВПУ-1 и ВПУ-2). Перевалка нефти осуществляется в штатном режиме.",
    },
    {
        "news_id": 802,
        "name": "Кейс 2: Текст БЕЗ терминов глоссария (проверка baseline и отсутствия галлюцинаций)",
        "title": "Встреча с ветеранами отрасли",
        "detail_text": "Вчера в центральном офисе состоялась ежегодная встреча с ветеранами. Участники обсудили историю развития компании и вручили памятные подарки.",
    },
    {
        "news_id": 803,
        "name": "Кейс 3: Насыщенный текст с 5+ терминами (промышленная безопасность, импортозамещение)",
        "title": "Итоги программы технического перевооружения",
        "detail_text": "В рамках программы импортозамещения и технического перевооружения компания повысила энергоэффективность и энергосбережение на всех объектах.",
    },
]


@pytest.mark.asyncio
async def test_glossary_robustness_cases(mock_llm_client: AsyncMock):
    from src.backend.services.glossary_service import GlossaryService

    glossary = GlossaryService()
    service = TranslationService(glossary=glossary, llm=mock_llm_client)

    for case in TEST_CASES:
        req = TranslationRequest(
            news_id=case["news_id"],
            title=case["title"],
            detail_text=case["detail_text"],
        )
        resp = await service.translate(req)

        assert resp.news_id == case["news_id"]
        assert resp.translated_title is not None
        assert resp.translated_detail_text is not None
        assert isinstance(resp.meta.terms_applied, list)
