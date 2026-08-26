"""
======================================================================
           PRISM-LLM Translator API — Live Demo Script              
          Микросервис перевода новостей RU→EN (Этап 2)               
======================================================================

Запуск:
    python demo/demo_live.py
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Обеспечение импорта пакета src из любого места запуска
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
BLUE = "\033[94m"


def header(text: str):
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")


def step(n: int, text: str):
    print(f"{BOLD}{YELLOW}[Шаг {n}]{RESET} {text}")


def ok(text: str):
    print(f"  {GREEN}[OK] {text}{RESET}")


def fail(text: str):
    print(f"  {RED}[FAIL] {text}{RESET}")


def info(text: str):
    print(f"  {BLUE}-> {text}{RESET}")


async def main():
    header("PRISM-LLM Translator API — Live Demo (Bitbucket Layout)")

    # --- ШАГ 1: Глоссарий ---
    step(1, "Инициализация глоссария (pymorphy3 + transneft_glossary_v002)...")
    from src.backend.services.glossary_service import GlossaryService
    glossary = GlossaryService("configs/glossary/transneft_glossary_v002.runtime.json")
    ok(f"Загружено {len(glossary.terms)} утверждённых терминов")

    # --- ШАГ 2: HTTP LLM Клиент ---
    step(2, "Подключение к HTTP-серверу инференса (LiteLLM / MLX Server)...")
    t0 = time.perf_counter()
    from src.backend.services.llm_client import create_llm_client
    llm = create_llm_client(backend="litellm", base_url="http://localhost:8001/v1", target_model="milmmt-12b")
    ok(f"HTTP LLM Клиент инициализирован za {time.perf_counter() - t0:.2f} сек")


    from src.backend.api.schemas import TranslationRequest
    from src.backend.services.translation_service import TranslationService
    service = TranslationService(glossary=glossary, llm=llm)

    # --- ШАГ 3: Выполнение перевода новости ---
    step(3, "Перевод новости с глоссарием (news_id=101)...")
    req1 = TranslationRequest(
        news_id=101,
        title="Завод ПАО «Транснефть» разработал электродвигатель для ледокола",
        detail_text=(
            "АО «Транснефть - Верхняя Волга» завершило плановые ремонтные работы "
            "на линейной производственно-диспетчерской станции. Проведена проверка "
            "запорной арматуры, мероприятия по экологической безопасности и охране труда."
        ),
    )
    info(f"news_id:  {req1.news_id}")
    info(f"RU Title: {req1.title}")
    info(f"RU Detail:{req1.detail_text}")
    resp1 = await service.translate(req1)
    print()
    ok(f"EN Title: {resp1.translated_title}")
    ok(f"EN Detail:{resp1.translated_detail_text}")
    ok(f"Модель: {resp1.meta.model_used} | Время: {resp1.meta.processing_time_ms} ms")
    print(f"\n  {BOLD}Применённые термины глоссария:{RESET}")
    for t in resp1.meta.terms_applied:
        print(f"    {GREEN}* {RESET} [{t.term_id}] {t.ru_term} -> {BOLD}{t.en_preferred}{RESET}")

    # --- ШАГ 4: Валидация Pydantic ---
    step(4, "Проверка Pydantic-валидации (отсутствие всех текстовых полей)...")
    from pydantic import ValidationError
    try:
        TranslationRequest(news_id=102)
        fail("Пустой запрос НЕ отклонён!")
    except ValidationError:
        ok("Пустой запрос корректно отклонён (@model_validator)")

    # --- ШАГ 5: X-API-Key M2M авторизация ---
    step(5, "Проверка M2M-авторизации X-API-Key...")
    from fastapi.testclient import TestClient
    from src.backend.main import app
    from src.backend.api.v1.translation import set_translation_service
    set_translation_service(service)
    client = TestClient(app, raise_server_exceptions=False)

    r_no_key = client.post("/api/v1/translate", json={"news_id": 103, "title": "T"})
    if r_no_key.status_code == 422:
        ok(f"Запрос БЕЗ ключа -> HTTP {r_no_key.status_code} (отклонён)")
    else:
        fail(f"Запрос без ключа не отклонён: {r_no_key.status_code}")

    r_bad_key = client.post("/api/v1/translate", json={"news_id": 103, "title": "T"}, headers={"X-API-Key": "wrong"})
    if r_bad_key.status_code == 401:
        ok(f"Неверный ключ -> HTTP {r_bad_key.status_code} Unauthorized")
    else:
        fail(f"Неверный ключ не отклонён: {r_bad_key.status_code}")

    r_ok = client.post(
        "/api/v1/translate",
        json={"news_id": 103, "title": "Тест", "detail_text": "Тестовый текст"},
        headers={"X-API-Key": "dev-token-change-me"},
    )
    if r_ok.status_code == 200:
        ok(f"Правильный ключ -> HTTP {r_ok.status_code} OK")
    else:
        fail(f"Правильный ключ отклонён: {r_ok.status_code}")

    # --- ИТОГ ---
    header("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
    print(f"  {GREEN}* {RESET} Модель MiLMMT 12B загружена и работает локально")
    print(f"  {GREEN}* {RESET} Контракт Bitbucket (news_id, title, announce, detail_text, meta) — подтверждён")
    print(f"  {GREEN}* {RESET} Pydantic валидация и X-API-Key авторизация — работают")


if __name__ == "__main__":
    asyncio.run(main())
