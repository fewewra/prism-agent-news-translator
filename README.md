# PRISM-LLM Translator API

Микросервис машинного перевода новостей ЕТП (RU→EN) с интеграцией корпоративного глоссария.

## Быстрый запуск

```bash
# 1. Создать виртуальное окружение
python3.12 -m venv .venv && source .venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt  # или poetry install

# 3. Скопировать конфигурацию
cp .env.example .env

# 4. Запустить сервис
uvicorn src.backend.main:app --reload

# 5. Проверить работу
curl http://localhost:8000/health
```

## API

- `POST /api/v1/translate` — перевод новости (требует `X-API-Key`)
- `GET /health` — healthcheck
- `GET /docs` — Swagger UI

## Тестирование

```bash
pytest tests/ -v
```

## Переключение LLM-бэкенда

В `.env` задаётся `LLM_BACKEND`:
- `local` — локальный инференс через MLX (MiLMMT 12B)
- `litellm` — вызов через LiteLLM-прокси (корпоративный контур)
