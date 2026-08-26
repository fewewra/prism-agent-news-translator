"""Гибридный LLM-клиент: локальный MLX или LiteLLM-прокси."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Абстрактный интерфейс LLM-клиента."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Сгенерировать ответ модели."""

    @abstractmethod
    def model_name(self) -> str:
        """Идентификатор модели."""


class LocalMLXClient(BaseLLMClient):
    """Локальный инференс через mlx-lm (Apple Silicon)."""

    def __init__(self, model_path: str) -> None:
        from mlx_lm import load

        logger.info("Загрузка локальной модели из %s ...", model_path)
        self._model, self._tokenizer = load(model_path)
        self._model_path = model_path
        logger.info("Модель загружена.")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        from mlx_lm import generate as mlx_generate

        prompt = (
            f"Translate this from Russian to English:\n"
            f"Russian: {system_prompt}\n\n{user_prompt}\n"
            f"English:"
        )
        result = await asyncio.to_thread(
            mlx_generate,
            self._model,
            self._tokenizer,
            prompt=prompt,
            max_tokens=512,
            verbose=False,
        )
        # Очистка от стоп-токенов
        for token in ("<eos>", "</s>", "<|im_end|>"):
            if result.endswith(token):
                result = result[: -len(token)].rstrip()
        return result.strip()

    def model_name(self) -> str:
        return "milmmt-12b-mlx-4bit-local"


class LiteLLMClient(BaseLLMClient):
    """HTTP-клиент к LiteLLM-прокси (OpenAI-совместимый API)."""

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
        response = await self._http.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._target_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 512,
            },
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def model_name(self) -> str:
        return self._target_model


class MockLLMClient(BaseLLMClient):
    """Мок LLM-клиент для Docker / CI тестирования без локальной модели."""

    def __init__(self, name: str = "mock-milmmt-12b") -> None:
        self._name = name

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "[Mock Translation] Successful text translation via PRISM-LLM API."

    def model_name(self) -> str:
        return self._name


def create_llm_client(
    *,
    backend: str,
    model_path: str = "",
    base_url: str = "",
    api_key: str = "",
    target_model: str = "",
) -> BaseLLMClient:
    """Фабрика LLM-клиента по значению LLM_BACKEND."""
    if backend == "local":
        try:
            return LocalMLXClient(model_path)
        except (ImportError, ModuleNotFoundError) as err:
            logger.warning(
                "Пакет mlx_lm недоступен в текущей ОС/контейнере (%s). "
                "Используется MockLLMClient для Docker/тестового окружения.",
                err,
            )
            return MockLLMClient("mock-milmmt-12b-local")
    if backend == "litellm":
        return LiteLLMClient(base_url, api_key, target_model)
    if backend == "mock":
        return MockLLMClient("mock-llm-testing")
    raise ValueError(f"Неизвестный LLM backend: {backend}")

