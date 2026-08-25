# Отчет о тестировании эндпоинта перевода (/api/v1/translate)

---

## 1. Сводка результатов автотестирования (Pytest)

- **Количество автотестов**: 22 / 22 пройдены успешно (100% PASS)
- **Время выполнения**: 0.42 сек
- **Файл конфигурации**: `pyproject.toml` (`testpaths = ["tests"]`)

### Список пройденных тест-кейсов:
```text
tests/test_api_translation.py::TestTranslateEndpoint::test_translate_success PASSED
tests/test_api_translation.py::TestTranslateEndpoint::test_translate_without_api_key PASSED
tests/test_api_translation.py::TestTranslateEndpoint::test_translate_wrong_api_key PASSED
tests/test_api_translation.py::TestTranslateEndpoint::test_translate_empty_text_fields PASSED
tests/test_api_translation.py::TestTranslateEndpoint::test_translate_with_custom_glossary PASSED
tests/test_api_translation.py::TestHealthEndpoint::test_health PASSED
tests/test_e2e_integration.py::TestE2ETranslationLifecycle::test_full_news_payload_with_title_announce_and_detail PASSED
tests/test_glossary_service.py::TestGlossaryService::test_loads_terms PASSED
tests/test_glossary_service.py::TestGlossaryService::test_match_exact_term PASSED
tests/test_glossary_service.py::TestGlossaryService::test_match_alias_inflected PASSED
tests/test_glossary_service.py::TestGlossaryService::test_match_empty_text PASSED
tests/test_glossary_service.py::TestGlossaryService::test_match_respects_limit PASSED
tests/test_glossary_service.py::TestGlossaryService::test_match_disabled_returns_empty PASSED
tests/test_prompt_service.py::TestPromptService::test_prompt_without_glossary PASSED
tests/test_prompt_service.py::TestPromptService::test_prompt_with_glossary PASSED
tests/test_prompt_service.py::TestPromptService::test_system_prompt_not_empty PASSED
tests/test_robustness.py::test_glossary_robustness_cases PASSED
tests/test_schemas.py::TestTranslationRequest::test_valid_request_with_title_and_detail PASSED
tests/test_schemas.py::TestTranslationRequest::test_valid_request_with_announce PASSED
tests/test_schemas.py::TestTranslationRequest::test_empty_text_fields_rejected PASSED
tests/test_schemas.py::TestTranslationRequest::test_custom_glossary_dictionary PASSED
tests/test_schemas.py::TestTranslationResponse::test_response_structure PASSED
```

---

## 2. Результаты исполнения запросов эндпоинта (JSON payload)

### Кейс 1: Healthcheck (`GET /health`)
- **Статус ответа**: `HTTP 200 OK`
- **Тело ответа**:
```json
{
  "status": "ok"
}
```

### Кейс 2: Перевод новости с ИТ-системами (`POST /api/v1/translate`, news_id=701)
- **Заголовок**: `X-API-Key: dev-token-change-me`
- **Входящее тело (Request)**:
```json
{
  "news_id": 701,
  "title": "Выделение вычислительных мощностей для Службы управления данными (СУД)",
  "announce": "В рамках обеспечения бесперебойной работы сервисов КИС УАТ и ЕППО выделены дополнительные ресурсы.",
  "detail_text": "Для СУД были выделены дополнительные вычислительные мощности, включающие Linux-сервер с тремя ускорителями NVIDIA A100."
}
```
- **Статус ответа**: `HTTP 200 OK`
- **Выходящее тело (Response)**:
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
        "term_id": "tn_0116",
        "ru_term": "Служба управления данными",
        "en_preferred": "Data Management Service (DMS)"
      },
      {
        "term_id": "tn_0117",
        "ru_term": "Корпоративная информационная система управления ИТ-архитектурой и требованиями",
        "en_preferred": "CIS ITARM (IT Architecture and Requirements Management System)"
      },
      {
        "term_id": "tn_0118",
        "ru_term": "Единая платформа производственной отчетности",
        "en_preferred": "UPRP (Unified Production Reporting Platform)"
      }
    ]
  }
}
```

### Кейс 3: Перевод с кастомным глоссарием (`POST /api/v1/translate`, news_id=102)
- **Входящее тело (Request)**:
```json
{
  "news_id": 102,
  "title": "Завод ПАО «Транснефть» разработал электродвигатель для ледокола",
  "detail_text": "АО «Транснефть - Верхняя Волга» завершило плановые ремонтные работы.",
  "glossary": {
    "электродвигатель": "electric motor unit",
    "ледокола": "icebreaker vessel"
  }
}
```
- **Статус ответа**: `HTTP 200 OK`
- **Выходящее тело (Response)**:
```json
{
  "news_id": 102,
  "translated_title": "Transneft plant has developed an electric motor unit for an icebreaker vessel.",
  "translated_announce": null,
  "translated_detail_text": "Transneft-Verkhnyaya Volga JSC has completed scheduled maintenance work.",
  "meta": {
    "model_used": "milmmt-12b-mlx-4bit-local",
    "processing_time_ms": 2910,
    "terms_applied": [
      {
        "term_id": "tn_0103",
        "ru_term": "ПАО «Транснефть»",
        "en_preferred": "Transneft"
      },
      {
        "term_id": "tn_0025",
        "ru_term": "ремонт",
        "en_preferred": "repair"
      },
      {
        "term_id": "custom_1",
        "ru_term": "электродвигатель",
        "en_preferred": "electric motor unit"
      },
      {
        "term_id": "custom_2",
        "ru_term": "ледокола",
        "en_preferred": "icebreaker vessel"
      }
    ]
  }
}
```

### Кейс 4: Проверка M2M авторизации (`HTTP 401`)
- **Заголовок**: `X-API-Key: invalid-key`
- **Статус ответа**: `HTTP 401 Unauthorized`
```json
{
  "detail": "Invalid or missing API key"
}
```

### Кейс 5: Валидация отсутствия текстовых полей (`HTTP 422`)
- **Входящее тело (Request)**: `{"news_id": 999}`
- **Статус ответа**: `HTTP 422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, Хотя бы одно из полей (title, announce, detail_text) должно быть заполнено",
      "input": {
        "news_id": 999
      }
    }
  ]
}
```
