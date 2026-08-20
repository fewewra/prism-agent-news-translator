"""Сквозные E2E тесты полного цикла перевода новостей."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.backend.api.v1.translation import set_translation_service
from src.backend.main import app
from src.backend.services.translation_service import TranslationService

API_KEY = "dev-token-change-me"


class TestE2ETranslationLifecycle:
    def test_full_news_payload_with_title_announce_and_detail(
        self, mock_glossary_path: str, mock_llm_client: AsyncMock
    ):
        from src.backend.services.glossary_service import GlossaryService

        glossary = GlossaryService(mock_glossary_path)
        service = TranslationService(glossary=glossary, llm=mock_llm_client)
        set_translation_service(service)

        client = TestClient(app, raise_server_exceptions=False)

        payload = {
            "news_id": 9901,
            "title": "Ремонт перекачивающей станции",
            "announce": "Завершены работы на объекте",
            "detail_text": "В ходе работ проведена проверка оборудования и промышленной безопасности.",
        }

        response = client.post(
            "/api/v1/translate",
            json=payload,
            headers={"X-API-Key": API_KEY},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["news_id"] == 9901
        assert data["translated_title"] == "Translated text in English."
        assert data["translated_announce"] == "Translated text in English."
        assert data["translated_detail_text"] == "Translated text in English."

        meta = data["meta"]
        assert meta["model_used"] == "mock-model"
        assert isinstance(meta["processing_time_ms"], int)
        assert meta["processing_time_ms"] >= 0
        assert len(meta["terms_applied"]) >= 2
