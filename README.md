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

### Пример запроса на перевод

```bash
curl -X POST http://localhost:8000/api/v1/translate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-token-change-me" \
  -d '{
    "news_id": 1001,
    "title": "ПАО «Транснефть» ввело в эксплуатацию новую перекачивающую станцию",
    "announce": "В рамках программы модернизации СУД завершены пусконаладочные работы.",
    "detail_text": "<p>Специалисты КИС УАТ проверили работу систем промышленной безопасности.</p>"
  }'
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

