"""Тесты сервиса глоссария."""

from src.backend.services.glossary_service import GlossaryService


class TestGlossaryService:
    def test_loads_terms(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        assert len(svc.terms) == 3

    def test_match_exact_term(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        matched = svc.match_terms("Проведён ремонт нефтепровода", limit=5)
        ids = [t.term_id for t in matched]
        assert "tn_test_001" in ids

    def test_match_alias_inflected(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        matched = svc.match_terms(
            "Обеспечение промышленной безопасности на перекачивающей станции",
            limit=5,
        )
        ids = [t.term_id for t in matched]
        assert "tn_test_002" in ids
        assert "tn_test_003" in ids

    def test_match_empty_text(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        matched = svc.match_terms("", limit=5)
        assert matched == []

    def test_match_respects_limit(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        matched = svc.match_terms(
            "Нефтепровод и промышленная безопасность на перекачивающей станции",
            limit=2,
        )
        assert len(matched) <= 2

    def test_match_disabled_returns_empty(self, mock_glossary_path: str):
        svc = GlossaryService(mock_glossary_path)
        matched = svc.match_terms("Нефтепровод", limit=0)
        assert matched == []
