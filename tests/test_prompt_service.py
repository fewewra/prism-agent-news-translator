"""Тесты формирования промптов."""

from src.backend.services.glossary_service import GlossaryTerm
from src.backend.services.prompt_service import SYSTEM_PROMPT, build_user_prompt


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
                en_forbidden=(),
                priority="mandatory",
                domain="test",
            )
        ]
        prompt = build_user_prompt("Ремонт нефтепровода", terms)
        assert "нефтепровод = oil pipeline" in prompt
        assert "terminology" in prompt.lower()
        assert "Russian source:" in prompt

    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 50
        assert "Translate" in SYSTEM_PROMPT
