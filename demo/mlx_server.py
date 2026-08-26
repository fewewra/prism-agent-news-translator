"""
======================================================================
  PRISM-LLM Translator — Standalone Local MLX HTTP Inference Server  
======================================================================

Изолированный HTTP-сервер инференса модели (порт 8001).
Предоставляет OpenAI-совместимый эндпоинт POST /v1/chat/completions.

Запуск:
    python demo/mlx_server.py
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mlx_server")

# Глобальные переменные инференс-модели
_model = None
_tokenizer = None
_has_mlx = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _model, _tokenizer, _has_mlx
    logger.info("Запуск автономного сервера инференса MLX на порту 8001...")
    try:
        from mlx_lm import load
        logger.info("Загрузка модели MiLMMT 12B из models/milmmt...")
        _model, _tokenizer = load("models/milmmt")
        _has_mlx = True
        logger.info("Модель MiLMMT 12B успешно загружена!")
    except Exception as err:
        logger.warning(
            "Не удалось загрузить локальную модель MLX (%s). "
            "Сервер будет работать в режиме HTTP-мока для тестирования.",
            err,
        )
        _has_mlx = False
    yield
    logger.info("Остановка сервера инференса.")


app = FastAPI(title="MLX Inference Server", version="1.0.0", lifespan=lifespan)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "milmmt-12b"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 512


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> dict:
    """OpenAI-совместимый эндпоинт /v1/chat/completions."""
    user_prompt = ""
    system_prompt = ""
    for msg in request.messages:
        if msg.role == "system":
            system_prompt = msg.content
        elif msg.role == "user":
            user_prompt = msg.content

    if _has_mlx and _model and _tokenizer:
        from mlx_lm import generate as mlx_generate

        prompt = f"System: {system_prompt}\nUser: {user_prompt}\nEnglish:"
        translated = await asyncio.to_thread(
            mlx_generate,
            _model,
            _tokenizer,
            prompt=prompt,
            max_tokens=request.max_tokens or 512,
            temp=request.temperature or 0.1,
            verbose=False,
        )
        for stop_token in ("<eos>", "</s>", "<|im_end|>"):
            if translated.endswith(stop_token):
                translated = translated[:-len(stop_token)].rstrip()
        translated_text = translated.strip()
    else:
        # Режим детерминированного ответа для автономного тестирования
        translated_text = (
            "[MLX HTTP Server] Successful translation of Russian source into English."
        )

    return {
        "id": "chatcmpl-mlx-001",
        "object": "chat.completion",
        "created": 1700000000,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": translated_text,
                },
                "finish_reason": "stop",
            }
        ],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
