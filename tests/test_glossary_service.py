"""Тесты stateless сервиса глоссария."""

from src.backend.services.glossary_service import GlossaryService, GlossaryTerm


class TestGlossaryService:
    def setup_method(self):
        self.svc = GlossaryService()
        self.sample_glossary = {
            "нефтепровод": "oil pipeline",
            "промышленная безопасность": "industrial safety",
            "перекачивающая станция": "pumping station",
        }

    def test_match_exact_term(self):
        matched = self.svc.match_terms(
            "Проведён ремонт нефтепровода", glossary_input=self.sample_glossary, limit=5
        )
        assert len(matched) == 1
        assert matched[0].ru_term == "нефтепровод"
        assert matched[0].en_preferred == "oil pipeline"

    def test_match_inflected_alias(self):
        matched = self.svc.match_terms(
            "Обеспечение промышленной безопасности на перекачивающей станции",
            glossary_input=self.sample_glossary,
            limit=5,
        )
        ru_terms = [t.ru_term for t in matched]
        assert "промышленная безопасность" in ru_terms
        assert "перекачивающая станция" in ru_terms

    def test_match_empty_text(self):
        matched = self.svc.match_terms("", glossary_input=self.sample_glossary, limit=5)
        assert matched == []

    def test_match_none_glossary(self):
        matched = self.svc.match_terms("Нефтепровод", glossary_input=None, limit=5)
        assert matched == []

    def test_match_respects_limit(self):
        matched = self.svc.match_terms(
            "Нефтепровод и промышленная безопасность на перекачивающей станции",
            glossary_input=self.sample_glossary,
            limit=2,
        )
        assert len(matched) <= 2

