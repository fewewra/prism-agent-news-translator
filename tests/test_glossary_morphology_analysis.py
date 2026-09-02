"""Анализ работы pymorphy3 и механизма сопоставления терминов глоссария.

Файл создан для проверки корректности лемматизации падежных форм,
сложных аббревиатур (ИСУРП, СУД) и выявления краевых ограничений (n-граммы > 4 слов).
"""

import pytest

from src.backend.services.glossary_service import GlossaryService


class TestGlossaryMorphologyAnalysis:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.svc = GlossaryService()

    def test_nezabudka_inflections_matching(self):
        """Проверка: сервис 'Незабудка' успешно сопоставляется в различных падежах и с кавычками."""
        glossary = {"Незабудка": "Nezabudka"}

        cases = [
            "Внедрение системы ИСУРП («Незабудка») переходит в финальную фазу.",
            "Специалисты работают в Незабудке над новыми модулями.",
            "Для подсистемы Незабудки выделены дополнительные ресурсы.",
            "Пользуемся «Незабудкой» каждый рабочий день.",
        ]

        for text in cases:
            matched = self.svc.match_terms(text, glossary_input=glossary)
            matched_ru = [t.ru_term for t in matched]
            assert "Незабудка" in matched_ru, f"Не найден термин 'Незабудка' в тексте: '{text}'"

    def test_isurp_acronym_inflections_matching(self):
        """Проверка: аббревиатура ИСУРП распознается в именительном падеже и при склонении."""
        glossary = {"ИСУРП": "ISURP System"}

        cases = [
            "В системе ИСУРП обновлены конфигурации.",
            "Пользователи ИСУРПа получили расширенный доступ.",
            "Развертывание системы ИСУРП («Незабудка») завершено.",
        ]

        for text in cases:
            matched = self.svc.match_terms(text, glossary_input=glossary)
            matched_ru = [t.ru_term for t in matched]
            assert "ИСУРП" in matched_ru, f"Не найден термин 'ИСУРП' в тексте: '{text}'"

    def test_long_terms_5_words_and_more_match_successfully(self):
        """Проверка: термины длиной более 4 слов успешно сопоставляются в GlossaryService."""
        glossary = {
            "автоматизированная система управления технологическими процессами": "automated process control system",
            "Корпоративная информационная система управления ИТ-архитектурой и требованиями": "CIS ITARM",
        }

        text = (
            "На объекте была модернизирована автоматизированная система "
            "управления технологическими процессами."
        )

        matched = self.svc.match_terms(text, glossary_input=glossary)
        matched_ru = [t.ru_term for t in matched]

        assert "автоматизированная система управления технологическими процессами" in matched_ru

    @pytest.mark.xfail(
        reason="Особенность pymorphy3: для неизвестных аббревиатур при склонении (КИС УАТом) первая гипотеза parse()[0] выдает ошибочную лемму 'уатом', а не 'уат'.",
        strict=True,
    )
    def test_colloquial_acronym_inflection_xfail(self):
        """Демонстрация ограничения pymorphy3: разговорные склонения аббревиатур могут не распознаваться."""
        glossary = {"КИС УАТ": "KIS UAT System"}
        text = "Интеграция с КИС УАТом завершена в срок."

        matched = self.svc.match_terms(text, glossary_input=glossary)
        matched_ru = [t.ru_term for t in matched]

        # Этот assert упадет (XFAIL), так как лемма 'уатом' != 'уат'
        assert "КИС УАТ" in matched_ru

    def test_glossary_service_does_not_mutate_translation_text(self):
        """Проверка архитектурной роли: GlossaryService возвращает канонический ru_term, а не форму из текста."""
        glossary = {"нефтепровод": "oil pipeline"}
        text = "Проводится ремонт нефтепроводов на севере."

        matched = self.svc.match_terms(text, glossary_input=glossary)
        assert len(matched) == 1
        # Pymorphy нашел слово, но вернул исходный словарный термин
        assert matched[0].ru_term == "нефтепровод"
        assert matched[0].en_preferred == "oil pipeline"
