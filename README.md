# PRISM-LLM Translator API (v1.0.0)

Изолированный stateless микросервис машинного перевода новостей ЕТП (RU→EN) для интеграции с веб-порталом 1С-Битрикс через REST API с поддержкой корпоративного глоссария.

## Технологический стек

- **Python**: 3.12
- **Фреймворк**: FastAPI + Uvicorn
- **Валидация**: Pydantic v2
- **Глоссарий**: `pymorphy3` (морфологический анализ и лемматизация)
- **Инференс**: Гибридный LLM-клиент (Local MLX / LiteLLM Proxy)
- **Тестирование**: Pytest (22 автотеста)
- **Контейнеризация**: Docker + docker-compose

---

## Быстрый запуск

### Вариант 1. Локальный запуск (Python 3.12)

```bash
# 1. Создать виртуальное окружение
python3.12 -m venv .venv && source .venv/bin/activate

# 2. Установить зависимости
pip install -e '.[dev]'

# 3. Настроить переменные окружения
cp .env.example .env

# 4. Запустить веб-сервер
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Проверить доступность
curl http://localhost:8000/health
```

### Вариант 2. Запуск в Docker

```bash
# Сборка и запуск контейнера
docker compose up --build
```

---

## API Эндпоинты

- `POST /api/v1/translate` — Перевод новости RU→EN (требует заголовок `X-API-Key`)
- `GET /health` — Проверка состояния сервиса (Healthcheck)
- `GET /docs` — Спецификация и интерактивная документация Swagger UI

### Пример запроса на перевод (из демо-набора ИТ-новостей)

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

### Пример ответа сервиса

```json
{
  "news_id": 701,
  "translated_title": "Allocation of Computing Capacities for the Data Management Service (DMS)",
  "translated_announce": "Additional resources have been allocated to ensure uninterrupted operation of CIS ITARM and UPRP services.",
  "translated_detail_text": "Additional computing capacities have been allocated for DMS, including a Linux server with three NVIDIA A100 accelerators and over 324 GB of RAM.",
  "meta": {
    "model_used": "milmmt-12b-mlx-4bit-local",
    "processing_time_ms": 2840,
    "terms_applied": [
      {
        "term_id": "tn_0042",
        "ru_term": "Служба управления данными",
        "en_preferred": "Data Management Service (DMS)"
      },
      {
        "term_id": "tn_0089",
        "ru_term": "КИС УАТ",
        "en_preferred": "CIS ITARM"
      },
      {
        "term_id": "tn_0091",
        "ru_term": "ЕППО",
        "en_preferred": "UPRP"
      }
    ]
  }
}
```

---

## Демонстрационные скрипты

- `python demo/demo_live.py` — Интерактивная демонстрация перевода новости
- `python demo/demo_it_abbreviations.py` — Сравнительный перевод ИТ-аббревиатур и названий служб
- `python demo/demo_local_translation.py` — Перевод через локальную модель MLX

---

## Тестирование

Запуск полных автотестов:

```bash
pytest
```

---

## Переключение LLM-бэкенда

В `.env` задаётся параметр `LLM_BACKEND`:
- `local` — Локальный инференс через MLX (MiLMMT 12B) для этапа разработки/демо
- `litellm` — Интеграция с LiteLLM-прокси (vLLM / SGLang) в защищенном контуре компании

