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
        url = self._base_url if self._base_url.endswith("/chat/completions") else f"{self._base_url}/chat/completions"
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
            if response.status_code >= 400:
                err_detail = response.text
                try:
                    err_json = response.json()
                    err_detail = err_json.get("error", err_json.get("message", response.text))
                except Exception:
                    pass
                logger.error("LM Studio HTTP %d error (%s): %s", response.status_code, url, err_detail)
                raise RuntimeError(
                    f"LLM API returned {response.status_code}: {err_detail}. "
                    "Убедитесь, что модель загружена в оперативную память в интерфейсе LM Studio (кнопка '+ Load Model')."
                )
            data: dict[str, Any] = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except RuntimeError:
            raise
        except Exception as err:
            # Автоматический фоллбэк для Docker-контейнеров, когда 127.0.0.1 не дотягивается до хоста
            if ("127.0.0.1" in url or "localhost" in url) and ("ConnectError" in str(type(err)) or "ConnectError" in str(err)):
                alt_url = url.replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")
                logger.warning("Не удалось подключиться к %s в Docker. Автоматически пробуем хост-адрес: %s", url, alt_url)
                try:
                    alt_resp = await self._http.post(alt_url, headers=headers, json=payload)
                    if alt_resp.status_code >= 400:
                        alt_detail = alt_resp.text
                        try:
                            alt_json = alt_resp.json()
                            alt_detail = alt_json.get("error", alt_json.get("message", alt_resp.text))
                        except Exception:
                            pass
                        raise RuntimeError(
                            f"LLM API returned {alt_resp.status_code}: {alt_detail}. "
                            "Убедитесь, что модель загружена в оперативную память в интерфейсе LM Studio (кнопка '+ Load Model')."
                        )
                    alt_data: dict[str, Any] = alt_resp.json()
                    return alt_data["choices"][0]["message"]["content"].strip()
                except Exception as alt_err:
                    err = alt_err

            logger.error("Ошибка при вызове LLM HTTP API (%s): %s", url, err)
            raise RuntimeError(f"LLM Inference HTTP error: {err}") from err

    def model_name(self) -> str:
        return self._target_model


def create_llm_client(
    *,
    base_url: str = "",
    api_key: str = "",
    target_model: str = "",
) -> BaseLLMClient:
    """Фабрика LLM-клиента для работы через HTTP REST (LM Studio / LiteLLM / vLLM)."""
    default_url = base_url or "http://127.0.0.1:1234/v1"
    default_model = target_model or "milmmt-46-12b-v0.1"
    return LiteLLMClient(
        base_url=default_url,
        api_key=api_key,
        target_model=default_model,
    )
