"""
======================================================================
  PRISM-LLM Translator — Bitrix Glossary Converter CLI Utility        
======================================================================

Инструмент стороны 1С-Битрикс / интеграции для конвертации файлов глоссария (.csv / .xlsx)
в JSON-словарь, готовый к отправке в пейлоаде запроса перевода (поле "glossary").

Примеры запуска:
    python scripts/parse_glossary.py -i data/glossary.csv -o data/bitrix_glossary.json
    python scripts/parse_glossary.py -i data/glossary.csv --format kv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def parse_csv_file(file_path: Path) -> Dict[str, str]:
    """Распарсить CSV-файл и вернуть словарь RU термин -> EN перевод."""
    glossary_dict: Dict[str, str] = {}
    content = file_path.read_text(encoding="utf-8-sig")
    
    # Определение разделителя по первой строке заголовка
    first_line = content.splitlines()[0] if content.splitlines() else ""
    delimiter = ";" if ";" in first_line else ("," if "," in first_line else "\t")
    
    reader = csv.DictReader(content.splitlines(), delimiter=delimiter)
    for row in reader:
        ru_term = (
            row.get("ru_term")
            or row.get("Русский термин")
            or row.get("ru")
            or row.get("Term")
            or ""
        ).strip()
        en_preferred = (
            row.get("en_preferred")
            or row.get("Английский перевод")
            or row.get("en")
            or row.get("Translation")
            or ""
        ).strip()
        
        if ru_term and en_preferred:
            glossary_dict[ru_term] = en_preferred
            
    return glossary_dict


def parse_excel_file(file_path: Path) -> Dict[str, str]:
    """Распарсить Excel (.xlsx/.xls) файл через openpyxl."""
    try:
        import openpyxl  # type: ignore
    except ImportError:
        print("Внимание: openpyxl не установлен. Попробуем распарсить файл как CSV...")
        return parse_csv_file(file_path)

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return {}

    headers = [str(cell or "").strip().lower() for cell in rows[0]]
    ru_idx = -1
    en_idx = -1

    for idx, h in enumerate(headers):
        if h in ("ru_term", "русский термин", "ru", "term"):
            ru_idx = idx
        elif h in ("en_preferred", "английский перевод", "en", "translation"):
            en_idx = idx

    if ru_idx == -1 or en_idx == -1:
        # Резервный вариант: столбцы 0 и 1
        ru_idx, en_idx = 0, 1

    glossary_dict: Dict[str, str] = {}
    for row in rows[1:]:
        if len(row) > max(ru_idx, en_idx):
            ru = str(row[ru_idx] or "").strip()
            en = str(row[en_idx] or "").strip()
            if ru and en:
                glossary_dict[ru] = en

    return glossary_dict


def main():
    parser = argparse.ArgumentParser(
        description="Конвертация CSV/Excel таблиц глоссария в JSON-словарь для Битрикс."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Путь к исходному CSV или XLSX файлу глоссария"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="data/bitrix_glossary.json",
        help="Путь для сохранения итогового JSON словаря",
    )
    parser.add_argument(
        "--format",
        choices=["kv", "array"],
        default="kv",
        help="Формат вывода: 'kv' (ключ-значение dict, по умолчанию) или 'array' (список объектов)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Ошибка: Исходный файл не найден по пути: {input_path}")
        sys.exit(1)

    print(f"Парсинг файла глоссария: {input_path}...")

    ext = input_path.suffix.lower()
    if ext in (".xlsx", ".xls"):
        glossary_dict = parse_excel_file(input_path)
    else:
        glossary_dict = parse_csv_file(input_path)

    if not glossary_dict:
        print("Ошибка: Не найдено валидных пар терминов в исходном файле!")
        sys.exit(1)

    if args.format == "kv":
        output_data: Any = glossary_dict
    else:
        output_data = [
            {"term_id": f"term_{idx}", "ru_term": ru, "en_preferred": en}
            for idx, (ru, en) in enumerate(glossary_dict.items(), start=1)
        ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Успешно сконвертировано {len(glossary_dict)} терминов в файл: {output_path}")


if __name__ == "__main__":
    main()

