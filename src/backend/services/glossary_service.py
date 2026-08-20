"""Сервис глоссария: загрузка терминов и поиск совпадений через pymorphy3."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pymorphy3


@dataclass(frozen=True, slots=True)
class GlossaryTerm:
    """Runtime-запись термина глоссария."""
    term_id: str
    ru_term: str
    en_preferred: str
    ru_aliases: tuple[str, ...]
    en_forbidden: tuple[str, ...]
    priority: str
    domain: str


class GlossaryService:
    """Загрузка глоссария и поиск терминов в тексте через лемматизацию."""

    def __init__(self, glossary_path: str) -> None:
        self._morph = pymorphy3.MorphAnalyzer()
        self._terms = self._load_glossary(glossary_path)
        self._lemma_index: dict[str, list[GlossaryTerm]] = self._build_lemma_index()

    def _load_glossary(self, path: str) -> tuple[GlossaryTerm, ...]:
        """Загрузить и валидировать runtime JSON глоссария."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        terms: list[GlossaryTerm] = []
        for raw in data.get("terms", []):
            if raw.get("status") != "approved":
                continue
            terms.append(GlossaryTerm(
                term_id=raw["term_id"],
                ru_term=raw["ru_term"],
                en_preferred=raw["en_preferred"],
                ru_aliases=tuple(raw.get("ru_aliases", [])),
                en_forbidden=tuple(raw.get("en_forbidden", [])),
                priority=raw.get("priority", "preferred"),
                domain=raw.get("domain", ""),
            ))
        return tuple(sorted(terms, key=lambda t: t.term_id))

    def _lemmatize_phrase(self, phrase: str) -> tuple[str, ...]:
        """Лемматизировать фразу через pymorphy3."""
        words = re.findall(r"[а-яёА-ЯЁ]+", phrase.lower())
        return tuple(self._morph.parse(w)[0].normal_form for w in words)

    def _build_lemma_index(self) -> dict[str, list[GlossaryTerm]]:
        """Построить индекс: ключевая лемма → список терминов."""
        index: dict[str, list[GlossaryTerm]] = {}
        for term in self._terms:
            phrases = [term.ru_term, *term.ru_aliases]
            for phrase in phrases:
                lemmas = self._lemmatize_phrase(phrase)
                if lemmas:
                    key = " ".join(lemmas)
                    index.setdefault(key, []).append(term)
        return index

    def _text_lemma_ngrams(self, text: str) -> set[str]:
        """Извлечь все лемма-нграммы (1..4 слова) из текста."""
        words = re.findall(r"[а-яёА-ЯЁ]+", text.lower())
        lemmas = [self._morph.parse(w)[0].normal_form for w in words]
        ngrams: set[str] = set()
        for n in range(1, min(5, len(lemmas) + 1)):
            for i in range(len(lemmas) - n + 1):
                ngrams.add(" ".join(lemmas[i : i + n]))
        return ngrams

    def match_terms(
        self, text: str, *, limit: int
    ) -> list[GlossaryTerm]:
        """Найти термины глоссария, присутствующие в тексте."""
        if limit <= 0:
            return []
        text_ngrams = self._text_lemma_ngrams(text)
        seen_ids: set[str] = set()
        matched: list[GlossaryTerm] = []
        priority_order = {"mandatory": 0, "preferred": 1, "optional": 2}
        candidates: list[tuple[int, str, GlossaryTerm]] = []
        for key, terms in self._lemma_index.items():
            if key in text_ngrams:
                for term in terms:
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

    @property
    def terms(self) -> tuple[GlossaryTerm, ...]:
        return self._terms
