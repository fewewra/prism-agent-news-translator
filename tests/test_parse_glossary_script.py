"""Тестирование CLI-утилиты парсинга таблицы глоссария scripts/parse_glossary.py."""

import json
from pathlib import Path

from scripts.parse_glossary import build_runtime_json, parse_csv_glossary


def test_parse_csv_glossary(tmp_path: Path):
    csv_file = tmp_path / "test_input.csv"
    csv_file.write_text(
        "Русский термин,Английский перевод,Синонимы,Приоритет\n"
        "Служба управления данными,Data Management Service (DMS),СУД;Службе управления данными,mandatory\n"
        "Единство,Unity,,preferred\n",
        encoding="utf-8-sig",
    )

    terms = parse_csv_glossary(csv_file)
    assert len(terms) == 2
    assert terms[0]["ru_term"] == "Служба управления данными"
    assert terms[0]["en_preferred"] == "Data Management Service (DMS)"
    assert terms[0]["ru_aliases"] == ["СУД", "Службе управления данными"]
    assert terms[0]["priority"] == "mandatory"


def test_build_runtime_json(tmp_path: Path):
    sample_terms = [
        {
            "term_id": "tn_0001",
            "ru_term": "Тест",
            "en_preferred": "Test",
            "ru_aliases": [],
            "status": "approved",
        }
    ]
    data = build_runtime_json(sample_terms)
    assert data["schema_version"] == "transneft-glossary-runtime-v002"
    assert len(data["terms"]) == 1
