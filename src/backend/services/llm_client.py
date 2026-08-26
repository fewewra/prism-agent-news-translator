"""Stateless LLM-клиент для взаимодействия с LiteLLM / vLLM / SGLang прокси через REST API."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Абстрактный интерфейс LLM-клиента."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Сгенерировать перевод текста через LLM."""

    @abstractmethod
    def model_name(self) -> str:
        """Идентификатор используемой модели."""


class LiteLLMClient(BaseLLMClient):
    """HTTP-клиент к LiteLLM/vLLM/SGLang прокси (OpenAI-совместимый API)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        target_model: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._target_model = target_model
        self._http = httpx.AsyncClient(timeout=120.0)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self._base_url}/chat/completions"
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 512,
        }

        try:
            response = await self._http.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as err:
            logger.error("Ошибка при вызове LLM HTTP API (%s): %s", url, err)
            raise RuntimeError(f"LLM Inference HTTP error: {err}") from err

    def model_name(self) -> str:
        return self._target_model


def create_llm_client(
    *,
    backend: str = "litellm",
    base_url: str = "",
    api_key: str = "",
    target_model: str = "",
    **_kwargs: Any,
) -> BaseLLMClient:
    """Фабрика LLM-клиента."""
    # Всегда создаём HTTP REST-клиент к серверу инференса
    default_url = base_url or "http://localhost:8001/v1"
    default_model = target_model or "milmmt-12b"
    return LiteLLMClient(
        base_url=default_url,
        api_key=api_key,
        target_model=default_model,
    )
