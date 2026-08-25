# Отчет о реальном прогоне модели MiLMMT 12B (/api/v1/translate)

---

## 1. Параметры запуска и инициализация

- **Локальная модель**: `models/milmmt` (`mlx-community/MiLMMT-46-12B-v0.1-4bit`)
- **Время загрузки весов модели**: `2.84 сек`
- **Глоссарий**: `configs/glossary/transneft_glossary_v002.runtime.json` (`122 термина`)
- **Время выполнения инференса**: `3955 ms` (`3.96 сек` на перевод `title` + `announce` + `detail_text`)

---

## 2. Логи прогона в консоли

```text
2026-08-25 10:40:02,094 [INFO] REAL_MODEL_RUNNER: === 1. Инициализация реального глоссария ===
2026-08-25 10:40:02,138 [INFO] REAL_MODEL_RUNNER: Загружено 122 терминов глоссария
2026-08-25 10:40:02,138 [INFO] REAL_MODEL_RUNNER: === 2. Загрузка реальной модели MiLMMT 12B из models/milmmt ===
2026-08-25 10:40:02,880 [INFO] src.backend.services.llm_client: Загрузка локальной модели из models/milmmt ...
2026-08-25 10:40:04,976 [INFO] src.backend.services.llm_client: Модель загружена за 2.84 сек.
2026-08-25 10:40:04,976 [INFO] REAL_MODEL_RUNNER: === 3. ВХОДЯЩИЙ ЗАПРОС РЕАЛЬНОГО ПЕРЕВОДА (news_id=701) ===
2026-08-25 10:40:04,976 [INFO] REAL_MODEL_RUNNER: title: Выделение вычислительных мощностей для Службы управления данными (СУД)
2026-08-25 10:40:04,976 [INFO] REAL_MODEL_RUNNER: announce: В рамках обеспечения бесперебойной работы сервисов КИС УАТ и ЕППО выделены дополнительные ресурсы.
2026-08-25 10:40:04,976 [INFO] REAL_MODEL_RUNNER: detail_text: Для СУД были выделены дополнительные вычислительные мощности, включающие Linux-сервер с тремя ускорителями NVIDIA A100.
2026-08-25 10:40:08,932 [INFO] src.backend.services.translation_service: Перевод новости news_id=701 выполнен за 3955 ms, примененено 3 терминов
```

---

## 3. Итоговый JSON-ответ реального инференса

```json
{
  "news_id": 701,
  "translated_title": "Allocation of computing resources for the Data Management Service (DMS)",
  "translated_announce": "Additional resources have been allocated to ensure the uninterrupted operation of the CIS ITARM and UPRP services.",
  "translated_detail_text": "Additional computing power was allocated for the Data Management Service (DMS), including a Linux server with three NVIDIA A100 accelerators.",
  "meta": {
    "model_used": "milmmt-12b-mlx-4bit-local",
    "processing_time_ms": 3955,
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
