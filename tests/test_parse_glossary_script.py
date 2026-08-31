"""Тестирование CLI-утилиты парсинга таблицы глоссария scripts/parse_glossary.py."""

from pathlib import Path

from scripts.parse_glossary import parse_csv_file


def test_parse_csv_glossary(tmp_path: Path):
    csv_file = tmp_path / "test_input.csv"
    csv_file.write_text(
        "Русский термин,Английский перевод,Синонимы,Приоритет\n"
        "Служба управления данными,Data Management Service (DMS),СУД;Службе управления данными,mandatory\n"
        "Единство,Unity,,preferred\n",
        encoding="utf-8-sig",
    )

    glossary_dict = parse_csv_file(csv_file)
    assert len(glossary_dict) == 2
    assert glossary_dict["Служба управления данными"] == "Data Management Service (DMS)"
    assert glossary_dict["Единство"] == "Unity"

