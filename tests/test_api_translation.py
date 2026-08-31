"""Интеграционные тесты API эндпоинта перевода."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.backend.api.v1.translation import set_translation_service
from src.backend.main import app
from src.backend.services.translation_service import TranslationService

API_KEY = "dev-token-change-me"


@pytest.fixture
def client(mock_llm_client: AsyncMock) -> TestClient:
    from src.backend.services.glossary_service import GlossaryService

    glossary = GlossaryService()
    service = TranslationService(glossary=glossary, llm=mock_llm_client)
    set_translation_service(service)
    return TestClient(app, raise_server_exceptions=False)


class TestTranslateEndpoint:
    def test_translate_success(self, client: TestClient):
        resp = client.post(
            "/api/v1/translate",
            json={
                "news_id": 501,
                "title": "Заголовок новости",
                "detail_text": "Текст новости",
            },
            headers={"X-API-Key": API_KEY},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["news_id"] == 501
        assert "translated_title" in data
        assert "translated_detail_text" in data
        assert "meta" in data
        assert data["meta"]["model_used"] == "mock-model"

    def test_translate_without_api_key(self, client: TestClient):
        resp = client.post(
            "/api/v1/translate",
            json={"news_id": 502, "title": "Заголовок"},
        )
        assert resp.status_code == 422  # missing required X-API-Key header

    def test_translate_wrong_api_key(self, client: TestClient):
        resp = client.post(
            "/api/v1/translate",
            json={"news_id": 503, "title": "Заголовок"},
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status_code == 401

    def test_translate_empty_text_fields(self, client: TestClient):
        resp = client.post(
            "/api/v1/translate",
            json={"news_id": 504},
            headers={"X-API-Key": API_KEY},
        )
        assert resp.status_code == 422  # validator requires title, announce, or detail_text

    def test_translate_with_custom_glossary(self, client: TestClient):
        resp = client.post(
            "/api/v1/translate",
            json={
                "news_id": 505,
                "title": "Ремонт нефтепровода",
                "detail_text": "Завершены работы на нефтепроводе",
                "glossary": {"нефтепровод": "oil pipeline"},
            },
            headers={"X-API-Key": API_KEY},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["news_id"] == 505
        assert len(data["meta"]["terms_applied"]) >= 1


class TestHealthEndpoint:
    def test_health(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
