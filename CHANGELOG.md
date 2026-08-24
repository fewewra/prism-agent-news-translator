# Changelog

## [1.0.0] — 2026-08-20

### Added
- Полное выравнивание API-контракта с целевым репозиторием Bitbucket (`news_id`, `announce`, `detail_text`, `glossary`, `meta`).
- Покрытие 22 автотестами Pytest (e2e интеграция, схемы Pydantic, API роутер, сервис глоссария).
- Полноценный Dockerfile с пробросом корпоративных сертификатов (`NEXUS_CERT`, `PYPI_INDEX_URL`) и манифест `docker-compose.yaml`.
- Интерактивные демо-скрипты перевода корпоративных новостей и ИТ-аббревиатур (`demo/demo_live.py`, `demo/demo_it_abbreviations.py`).
- Документация API: OpenAPI спецификация (`docs/api_contract.json`), Mermaid диаграммы вызовов (`docs/assets/`).

## [0.1.0] — 2026-08-14

### Added
- Инициализация FastAPI микросервиса с эндпоинтом `POST /api/v1/translate`
- Гибридный LLM-клиент (Local MLX / LiteLLM-прокси)
- Глоссарий v002 (122 термина) с лемматизацией `pymorphy3`
- M2M-авторизация через `X-API-Key`

