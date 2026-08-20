# Changelog

## [0.1.0] — 2026-08-14

### Added
- FastAPI микросервис с эндпоинтом `POST /api/v1/translate`
- Гибридный LLM-клиент (Local MLX / LiteLLM-прокси)
- Глоссарий Транснефти v002 (115 терминов) с лемматизацией pymorphy3
- M2M-авторизация через X-API-Key
- Pydantic v2 валидация входных данных
- 24 автотеста (Pytest)
- Dockerfile с поддержкой корпоративных сертификатов
- OpenAPI контракт (docs/api_contract.json)
