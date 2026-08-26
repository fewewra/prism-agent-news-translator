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
    """Собрать пользовательский промпт с опциональным блоком глоссария."""
    blocks: list[str] = []
    if matched_terms:
        glossary_lines = "\n".join(
            f"{term.ru_term} = {term.en_preferred}" for term in matched_terms
        )
        blocks.append(
            "Use the terminology below only when a corresponding "
            "Russian term occurs. It is service context and must not "
            "be copied into the answer.\n" + glossary_lines
        )
    blocks.append("Russian source:\n" + text + "\nEnglish translation:")
    return "\n\n".join(blocks)
