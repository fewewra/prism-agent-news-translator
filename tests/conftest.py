"""Фикстуры для тестирования."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_glossary_path(tmp_path: Path) -> str:
    """Создать минимальный тестовый глоссарий."""
    glossary = {
        "schema_version": "transneft-glossary-runtime-v002",
        "glossary_id": "test_glossary",
        "terms": [
            {
                "term_id": "tn_test_001",
                "ru_term": "нефтепровод",
                "en_preferred": "oil pipeline",
                "ru_aliases": ["нефтепровода"],
                "en_allowed": [],
                "en_forbidden": [],
                "domain": "pipeline_operations",
                "priority": "mandatory",
                "case_sensitive": False,
                "whole_word": True,
                "status": "approved",
                "notes": "",
            },
            {
                "term_id": "tn_test_002",
                "ru_term": "перекачивающая станция",
                "en_preferred": "pumping station",
                "ru_aliases": ["перекачивающей станции"],
                "en_allowed": [],
                "en_forbidden": [],
                "domain": "pumping_stations",
                "priority": "mandatory",
                "case_sensitive": False,
                "whole_word": True,
                "status": "approved",
                "notes": "",
            },
            {
                "term_id": "tn_test_003",
                "ru_term": "промышленная безопасность",
                "en_preferred": "industrial safety",
                "ru_aliases": ["промышленной безопасности"],
                "en_allowed": [],
                "en_forbidden": [],
                "domain": "industrial_safety",
                "priority": "preferred",
                "case_sensitive": False,
                "whole_word": True,
                "status": "approved",
                "notes": "",
            },
        ],
    }
    path = tmp_path / "test_glossary.json"
    path.write_text(json.dumps(glossary, ensure_ascii=False), encoding="utf-8")
    return str(path)


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Мок LLM-клиента для тестов без реальной модели."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Translated text in English.")
    client.model_name = lambda: "mock-model"
    return client
