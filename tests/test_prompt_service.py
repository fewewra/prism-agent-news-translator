"""Тесты формирования промптов и загрузки внешнего файла системного промпта."""

import pytest
from pathlib import Path

from src.backend.services.glossary_service import GlossaryTerm
from src.backend.services.prompt_service import (
    SYSTEM_PROMPT,
    build_user_prompt,
    load_system_prompt,
)


class TestPromptService:
    def test_prompt_without_glossary(self):
        prompt = build_user_prompt("Текст новости", [])
        assert "Russian source:" in prompt
        assert "Текст новости" in prompt
        assert "English translation:" in prompt
        assert "terminology" not in prompt.lower()

    def test_prompt_with_glossary(self):
        terms = [
            GlossaryTerm(
                term_id="t1",
                ru_term="нефтепровод",
                en_preferred="oil pipeline",
                ru_aliases=(),
                priority="mandatory",
                domain="test",
            )
        ]
        prompt = build_user_prompt("Ремонт нефтепровода", terms)
        assert "- нефтепровод => oil pipeline" in prompt
        assert "mandatory corporate glossary" in prompt.lower()
        assert "Russian source:" in prompt

    def test_system_prompt_loaded_from_file(self):
        assert len(SYSTEM_PROMPT) > 50
        assert "Translate" in SYSTEM_PROMPT

    def test_load_system_prompt_raises_file_not_found(self, tmp_path: Path):
        non_existent_file = tmp_path / "non_existent.md"
        with pytest.raises(FileNotFoundError, match="Не найден файл системного промпта"):
            load_system_prompt(non_existent_file)

    def test_load_system_prompt_raises_on_empty_file(self, tmp_path: Path):
        empty_file = tmp_path / "empty_prompt.md"
        empty_file.write_text("   \n ", encoding="utf-8")
        with pytest.raises(FileNotFoundError, match="пуст"):
            load_system_prompt(empty_file)
