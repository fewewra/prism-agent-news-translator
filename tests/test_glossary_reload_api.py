"""Тестирование эндпоинта горячей перезагрузки глоссария POST /api/v1/glossary/reload."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.backend.api.v1.translation import set_translation_service
from src.backend.main import app
from src.backend.services.glossary_service import GlossaryService
from src.backend.services.translation_service import TranslationService


def test_glossary_service_reload(mock_glossary_path: str, tmp_path: Path):
    service = GlossaryService(mock_glossary_path)
    assert len(service.terms) == 3

    # Создаём новый файл глоссария с 1 термином
    new_data = {
        "schema_version": "v2",
        "terms": [
            {
                "term_id": "tn_new_01",
                "ru_term": "компрессор",
                "en_preferred": "compressor",
                "ru_aliases": [],
                "priority": "mandatory",
                "status": "approved",
            }
        ],
    }
    new_path = tmp_path / "new_glossary.json"
    new_path.write_text(json.dumps(new_data, ensure_ascii=False), encoding="utf-8")

    # Перезагружаем на новый путь
    count = service.reload(str(new_path))
    assert count == 1
    assert service.terms[0].term_id == "tn_new_01"


def test_api_reload_glossary_unauthorized(mock_glossary_path: str):
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/api/v1/glossary/reload", headers={"X-API-Key": "wrong-token"})
    assert resp.status_code == 401


def test_api_reload_glossary_success(mock_glossary_path: str, mock_llm_client: AsyncMock):
    glossary_svc = GlossaryService(mock_glossary_path)
    trans_svc = TranslationService(glossary=glossary_svc, llm=mock_llm_client)
    set_translation_service(trans_svc)

    client = TestClient(app)
    resp = client.post("/api/v1/glossary/reload", headers={"X-API-Key": "dev-token-change-me"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["terms_count"] == 3
