# PRISM-LLM Translator API (v1.0.0)

Изолированный **stateless микросервис** машинного перевода новостей ЕТП (RU→EN) для интеграции с веб-порталом 1С-Битрикс через REST API с поддержкой корпоративного глоссария.

## Технологический стек

- **Python**: 3.12
- **Фреймворк**: FastAPI + Uvicorn
- **Валидация**: Pydantic v2
- **Глоссарий**: `pymorphy3` (морфологический анализ и лемматизация н-грамм)
- **Инференс**: Stateless HTTP-клиент к OpenAI-совместимому API (LiteLLM / vLLM / SGLang / MLX HTTP Server)
- **Тестирование**: Pytest (29 автотестов)
- **Контейнеризация**: Docker + docker-compose

---

## Архитектура разделения ответственности (Separation of Concerns)

1. **`translator-api` (Порт 8000)**: Легковесный stateless микросервис бизнес-логики. Занимается авторизацией (`X-API-Key`), валидацией схем Bitbucket (`news_id`, `title`, `announce`, `detail_text`), лемматизацией глоссария и отправкой асинхронных HTTP-запросов к серверу инференса.
2. **LLM Inference Server (Порт 8001 / LiteLLM)**: Выделенный отдельный сервер инференса модели (vLLM / SGLang в контуре или `demo/mlx_server.py` при локальной разработке).

---

## Быстрый запуск

### Вариант 1. Локальный запуск (2 сервиса)

```bash
# 1. Активировать виртуальное окружение и установить зависимости
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env

# 2. Окно 1: Запустить автономный HTTP-сервер инференса модели (Порт 8001)
python demo/mlx_server.py

# 3. Окно 2: Запустить основной микросервис перевода (Порт 8000)
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Проверить доступность
curl http://localhost:8000/health
```

### Вариант 2. Запуск в Docker

```bash
# Сборка и запуск контейнера
docker compose up --build
```

---

## Автоматизация работы с глоссарием

### 1. Первичный парсинг таблицы заказчика (Excel / CSV $\rightarrow$ JSON)

Для конвертациисходной таблицы заказчика (`.csv` / `.xlsx`) в runtime JSON формат используется CLI-утилита:

```bash
python scripts/parse_glossary.py \
  --input data/glossary.csv \
  --output configs/glossary/transneft_glossary_v002.runtime.json
```

### 2. Горячая перезагрузка глоссария без перезапуска сервиса

Разработчики Битрикса или скрипт автоматизации могут обновить файл на сервере и мгновенно перестроить лемма-индекс сервиса:

```bash
curl -X POST http://localhost:8000/api/v1/glossary/reload \
  -H "X-API-Key: dev-token-change-me"
```

---

## API Эндпоинты

- `POST /api/v1/translate` — Перевод новости RU→EN (требует `X-API-Key`)
- `POST /api/v1/glossary/reload` — Горячая перезагрузка глоссария с диска (требует `X-API-Key`)
- `GET /health` — Проверка состояния сервиса (Healthcheck)
- `GET /docs` — Спецификация и интерактивная документация Swagger UI

### Пример запроса на перевод

```bash
curl -X POST http://localhost:8000/api/v1/translate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-token-change-me" \
  -d '{
    "news_id": 701,
    "title": "Выделение вычислительных мощностей для Службы управления данными (СУД)",
    "announce": "В рамках обеспечения бесперебойной работы сервисов КИС УАТ и ЕППО выделены дополнительные ресурсы.",
    "detail_text": "Для СУД были выделены дополнительные вычислительные мощности, включающие Linux-сервер с тремя ускорителями NVIDIA A100 и более чем 324 ГБ ОЗУ."
  }'
```

---

## Демонстрационные скрипты

- `python demo/demo_live.py` — Интерактивная демонстрация перевода новости
- `python demo/demo_it_abbreviations.py` — Сравнительный перевод ИТ-аббревиатур и названий служб
- `python demo/mlx_server.py` — Изолированный HTTP REST-сервер инференса (Порт 8001)

---

## Тестирование

Запуск автотестов Pytest:

```bash
pytest
```
