"""
======================================================================
  PRISM-LLM Translator — Glossary Parser CLI Utility                  
======================================================================

Скрипт конвертации исходных файлов глоссария заказчика (.xlsx / .csv)
в валидированный runtime JSON формат для микросервиса перевода.

Запуск:
    python scripts/parse_glossary.py --input data/glossary.csv --output configs/glossary/transneft_glossary_v002.runtime.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def parse_csv_glossary(file_path: Path) -> List[Dict[str, Any]]:
    """Распарсить CSV-файл с глоссарием."""
    terms: List[Dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            ru_term = (row.get("ru_term") or row.get("Русский термин") or "").strip()
            en_preferred = (row.get("en_preferred") or row.get("Английский перевод") or "").strip()
            if not ru_term or not en_preferred:
                continue

            aliases_raw = row.get("ru_aliases") or row.get("Синонимы") or ""
            aliases = [a.strip() for a in aliases_raw.split(";") if a.strip()]

            priority = (row.get("priority") or row.get("Приоритет") or "mandatory").strip().lower()
            if priority not in ("mandatory", "preferred", "optional"):
                priority = "mandatory"

            domain = (row.get("domain") or row.get("Область") or "general").strip()

            terms.append(
                {
                    "term_id": f"tn_{idx:04d}",
                    "ru_term": ru_term,
                    "en_preferred": en_preferred,
                    "ru_aliases": aliases,
                    "en_allowed": [],
                    "en_forbidden": [],
                    "domain": domain,
                    "priority": priority,
                    "case_sensitive": False,
                    "whole_word": True,
                    "status": "approved",
                    "notes": "",
                }
            )
    return terms


def build_runtime_json(terms: List[Dict[str, Any]], glossary_id: str = "transneft_glossary_v002") -> Dict[str, Any]:
    """Сформировать валидную JSON-структуру рантайм-глоссария."""
    return {
        "schema_version": "transneft-glossary-runtime-v002",
        "glossary_id": glossary_id,
        "terms": terms,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Конвертация Excel/CSV таблиц глоссария в runtime JSON формат."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Путь к исходному CSV/XLSX файлу глоссария"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="configs/glossary/transneft_glossary_v002.runtime.json",
        help="Путь для сохранения итогового runtime JSON",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Ошибка: Исходный файл не найден по пути: {input_path}")
        sys.exit(1)

    print(f"Парсинг файла глоссария: {input_path}...")

    if input_path.suffix.lower() == ".csv":
        terms = parse_csv_glossary(input_path)
    else:
        # Резервный формат для CSV/JSON файлов
        print("Формат не поддерживается напрямую без openpyxl, парсим как CSV...")
        terms = parse_csv_glossary(input_path)

    if not terms:
        print("Ошибка: Не найдено валидных терминов в исходном файле!")
        sys.exit(1)

    runtime_data = build_runtime_json(terms)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(runtime_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f" Успешно создано {len(terms)} терминов в файле: {output_path}")


if __name__ == "__main__":
    main()
