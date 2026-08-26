"""Формирование системного и пользовательского промптов."""

from __future__ import annotations

from typing import Sequence

from src.backend.services.glossary_service import GlossaryTerm

from pathlib import Path

DEFAULT_SYSTEM_PROMPT_PATH = Path("configs/prompts/system_prompt.md")


def load_system_prompt(path: Path | str = DEFAULT_SYSTEM_PROMPT_PATH) -> str:
    """Загрузить системный промпт из внешнего файла."""
    file_path = Path(path)
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8").strip()
        if content:
            return content
    return (
        "Translate the following Russian text into English. "
        "Preserve the complete meaning, numbers, dates, percentages, units, "
        "abbreviations, company names and facility names. "
        "Do not add or omit information. Return only the English translation "
        "without explanations, headings or the Russian source."
    )


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
