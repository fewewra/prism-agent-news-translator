"""Формирование системного и пользовательского промптов."""

from __future__ import annotations

from typing import Sequence

from src.backend.services.glossary_service import GlossaryTerm

SYSTEM_PROMPT = (
    "Translate the following Russian text into English. "
    "Preserve the complete meaning, numbers, dates, percentages, units, "
    "abbreviations, company names and facility names. "
    "Do not add or omit information. Return only the English translation "
    "without explanations, headings or the Russian source."
)


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
