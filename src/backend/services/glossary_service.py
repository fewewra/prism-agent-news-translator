"""Stateless сервис глоссария: поиск совпадений терминов в тексте через pymorphy3."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Sequence, Union

import pymorphy3


@dataclass(frozen=True, slots=True)
class GlossaryTerm:
    """Runtime-запись термина глоссария."""

    term_id: str
    ru_term: str
    en_preferred: str
    ru_aliases: tuple[str, ...] = ()
    priority: str = "mandatory"
    domain: str = "custom"


class GlossaryService:
    """Stateless сервис глоссария.

    Инициализирует pymorphy3 морфологический анализатор. Не хранит термины между запросами.
    """

    def __init__(self) -> None:
        self._morph = pymorphy3.MorphAnalyzer()

    def _lemmatize_phrase(self, phrase: str) -> tuple[str, ...]:
        """Лемматизировать фразу через pymorphy3."""
        words = re.findall(r"[а-яёА-ЯЁa-zA-Z0-9]+", phrase.lower())
        lemmas = []
        for w in words:
            parsed = self._morph.parse(w)
            lemmas.append(parsed[0].normal_form if parsed else w)
        return tuple(lemmas)

    def _text_lemma_ngrams(self, text: str) -> set[str]:
        """Извлечь все лемма-нграммы (1..4 слова) из исходного текста."""
        words = re.findall(r"[а-яёА-ЯЁa-zA-Z0-9]+", text.lower())
        lemmas = []
        for w in words:
            parsed = self._morph.parse(w)
            lemmas.append(parsed[0].normal_form if parsed else w)

        ngrams: set[str] = set()
        for n in range(1, min(5, len(lemmas) + 1)):
            for i in range(len(lemmas) - n + 1):
                ngrams.add(" ".join(lemmas[i : i + n]))
        return ngrams

    def _normalize_input_terms(
        self, glossary_input: Union[Dict[str, str], Sequence[GlossaryTerm], Sequence[dict], None]
    ) -> list[GlossaryTerm]:
        """Преобразовать различные формы входящего глоссария в единый список GlossaryTerm."""
        if not glossary_input:
            return []

        terms: list[GlossaryTerm] = []

        if isinstance(glossary_input, dict):
            for idx, (ru_term, en_pref) in enumerate(glossary_input.items(), start=1):
                if not ru_term or not en_pref:
                    continue
                terms.append(
                    GlossaryTerm(
                        term_id=f"term_{idx}",
                        ru_term=ru_term.strip(),
                        en_preferred=en_pref.strip(),
                    )
                )
        elif isinstance(glossary_input, (list, tuple)):
            for idx, item in enumerate(glossary_input, start=1):
                if isinstance(item, GlossaryTerm):
                    terms.append(item)
                elif isinstance(item, dict):
                    ru = item.get("ru_term") or item.get("ru") or ""
                    en = item.get("en_preferred") or item.get("en") or ""
                    if ru and en:
                        terms.append(
                            GlossaryTerm(
                                term_id=str(item.get("term_id", f"term_{idx}")),
                                ru_term=ru.strip(),
                                en_preferred=en.strip(),
                                ru_aliases=tuple(item.get("ru_aliases", ())),
                                priority=item.get("priority", "mandatory"),
                                domain=item.get("domain", "custom"),
                            )
                        )
        return terms

    def match_terms(
        self,
        text: str,
        glossary_input: Union[Dict[str, str], Sequence[GlossaryTerm], Sequence[dict], None] = None,
        *,
        limit: int = 10,
    ) -> list[GlossaryTerm]:
        """Найти только те термины из переданного глоссария, которые физически встречаются в тексте.

        Создаёт временный индекс в рамках стека функции, по завершении данные полностью удаляются из памяти.
        """
        if not text or limit <= 0:
            return []

        terms = self._normalize_input_terms(glossary_input)
        if not terms:
            return []

        # Временный лемма-индекс для входящих терминов (scope запроса)
        lemma_index: dict[str, list[GlossaryTerm]] = {}
        for term in terms:
            phrases = [term.ru_term, *term.ru_aliases]
            for phrase in phrases:
                lemmas = self._lemmatize_phrase(phrase)
                if lemmas:
                    key = " ".join(lemmas)
                    lemma_index.setdefault(key, []).append(term)

        text_ngrams = self._text_lemma_ngrams(text)
        seen_ids: set[str] = set()
        matched: list[GlossaryTerm] = []

        priority_order = {"mandatory": 0, "preferred": 1, "optional": 2}
        candidates: list[tuple[int, str, GlossaryTerm]] = []

        for key, indexed_terms in lemma_index.items():
            if key in text_ngrams:
                for term in indexed_terms:
                    if term.term_id not in seen_ids:
                        seen_ids.add(term.term_id)
                        candidates.append((
                            priority_order.get(term.priority, 9),
                            term.term_id,
                            term,
                        ))

        candidates.sort()
        for _, _, term in candidates[:limit]:
            matched.append(term)

        return matched

