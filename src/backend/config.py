"""Конфигурация приложения через переменные окружения."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- General App ---
    environment: Literal["dev", "prod", "test"] = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # --- Security & Authorization ---
    bitrix_auth_token: str = "dev-token-change-me"

    # --- LLM Backend Switch ---
    llm_backend: Literal["local", "litellm"] = "local"

    # --- LiteLLM (for corporate perimeter) ---
    litellm_base_url: str = ""
    litellm_api_key: str = ""
    target_model_name: str = "qwen/qwen"

    # --- Local MLX (for local development) ---
    local_model_path: str = "models/milmmt"

    # --- Glossary ---
    glossary_path: str = "configs/glossary/transneft_glossary_v002.runtime.json"

    # --- Observability (Langfuse) ---
    langfuse_host: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""


settings = Settings()
