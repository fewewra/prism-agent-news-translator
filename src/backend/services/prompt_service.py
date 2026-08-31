"""Формирование системного и пользовательского промптов."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.backend.services.glossary_service import GlossaryTerm

DEFAULT_SYSTEM_PROMPT_PATH = Path("configs/prompts/system_prompt.md")


def load_system_prompt(path: Path | str = DEFAULT_SYSTEM_PROMPT_PATH) -> str:
    """Загрузить системный промпт из внешнего файла.

    Raises:
        FileNotFoundError: Если файл промпта отсутствует или пуст.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Не найден файл системного промпта по пути: {file_path.resolve()}"
        )

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise FileNotFoundError(
            f"Файл системного промпта {file_path.resolve()} пуст"
        )

    return content


# Системный промпт загружается из единого внешнего источника истины
SYSTEM_PROMPT = load_system_prompt()


def build_user_prompt(
    text: str,
    matched_terms: Sequence[GlossaryTerm],
) -> str:
    """Собрать пользовательский промпт с универсальной строгой инструкцией по глоссарию."""
    blocks: list[str] = []
    if matched_terms:
        unique_pairs: dict[str, str] = {}
        for term in matched_terms:
            unique_pairs[term.ru_term] = term.en_preferred

        glossary_lines = "\n".join(
            f"- {ru} => {en}" for ru, en in unique_pairs.items()
        )
        blocks.append(
            "MANDATORY CORPORATE GLOSSARY (Strictly enforce these exact translations whenever a corresponding Russian term appears in the text):\n"
            + glossary_lines
        )
    blocks.append("Russian source:\n" + text + "\nEnglish translation:")
    return "\n\n".join(blocks)
