"""Pydantic v2 схемы запроса и ответа перевода, выровненные с контрактом Bitbucket."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class TranslationRequest(BaseModel):
    """Входящий запрос на перевод новости из 1С-Битрикс."""

    news_id: int = Field(
        ..., description="Уникальный идентификатор новости в Битрикс для сквозной трассировки"
    )
    title: Optional[str] = Field(None, description="Заголовок новости")
    announce: Optional[str] = Field(None, description="Краткий анонс новости")
    detail_text: Optional[str] = Field(
        None, description="Полный текст новости с HTML-разметкой"
    )
    glossary: Optional[Dict[str, str]] = Field(
        default=None,
        description="Кастомный словарь терминов. Ключ — русский термин, значение — английский перевод",
    )

    @model_validator(mode="after")
    def check_at_least_one_text_field(self) -> TranslationRequest:
        """Проверка: хотя бы одно текстовое поле должно быть заполнено."""
        if not any([self.title, self.announce, self.detail_text]):
            raise ValueError(
                "Хотя бы одно из полей (title, announce, detail_text) должно быть заполнено"
            )
        return self


class GlossaryTermApplied(BaseModel):
    """Информация о применённом термине глоссария."""

    term_id: str
    ru_term: str
    en_preferred: str


class TranslationMeta(BaseModel):
    """Метаданные ответа перевода."""

    model_used: str = Field(..., description="Название ИИ-модели, выполнившей перевод")
    processing_time_ms: int = Field(
        ..., description="Время обработки запроса в миллисекундах"
    )
    terms_applied: List[GlossaryTermApplied] = Field(
        default_factory=list, description="Термины глоссария, применённые при переводе"
    )


class TranslationResponse(BaseModel):
    """Ответ на запрос перевода."""

    news_id: int = Field(..., description="Идентификатор новости из запроса")
    translated_title: Optional[str] = Field(
        None, description="Переведенный заголовок"
    )
    translated_announce: Optional[str] = Field(
        None, description="Переведенный анонс"
    )
    translated_detail_text: Optional[str] = Field(
        None, description="Переведенный полный текст"
    )
    meta: TranslationMeta
