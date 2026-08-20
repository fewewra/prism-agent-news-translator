"""Тесты Pydantic-схем Bitbucket контракта."""

import pytest
from pydantic import ValidationError

from src.backend.api.schemas import (
    TranslationMeta,
    TranslationRequest,
    TranslationResponse,
)


class TestTranslationRequest:
    def test_valid_request_with_title_and_detail(self):
        req = TranslationRequest(
            news_id=1001,
            title="Заголовок новости",
            detail_text="Полный текст новости",
        )
        assert req.news_id == 1001
        assert req.title == "Заголовок новости"
        assert req.detail_text == "Полный текст новости"
        assert req.announce is None

    def test_valid_request_with_announce(self):
        req = TranslationRequest(
            news_id=1002,
            announce="Краткий анонс новости",
        )
        assert req.news_id == 1002
        assert req.announce == "Краткий анонс новости"

    def test_empty_text_fields_rejected(self):
        """Хотя бы одно из полей (title, announce, detail_text) должно быть заполнено."""
        with pytest.raises(ValidationError):
            TranslationRequest(news_id=1003)

    def test_custom_glossary_dictionary(self):
        req = TranslationRequest(
            news_id=1004,
            title="Заголовок",
            glossary={"СУД": "Data Management Service"},
        )
        assert req.glossary == {"СУД": "Data Management Service"}


class TestTranslationResponse:
    def test_response_structure(self):
        resp = TranslationResponse(
            news_id=1001,
            translated_title="Translated Title",
            translated_detail_text="Translated Detail",
            meta=TranslationMeta(
                model_used="milmmt-12b-local",
                processing_time_ms=120,
            ),
        )
        assert resp.news_id == 1001
        assert resp.translated_title == "Translated Title"
        assert resp.meta.model_used == "milmmt-12b-local"
        assert resp.meta.processing_time_ms == 120
        assert resp.meta.terms_applied == []
