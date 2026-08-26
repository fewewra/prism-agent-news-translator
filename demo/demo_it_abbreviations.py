"""
======================================================================
        PRISM-LLM Translator API — IT Systems & Abbreviation Demo     
       Сравнительное тестирование режимов перевода новостей ЕТП      
======================================================================

Запуск:
    python demo/demo_it_abbreviations.py
"""

import asyncio
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
MAGENTA = "\033[95m"


def header(text: str):
    print(f"\n{BOLD}{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 80}{RESET}\n")


def news_box(news_id: int, title: str, body: str):
    print(f"{BOLD}{MAGENTA}[ВХОДЯЩИЕ ДАННЫЕ (news_id={news_id})]:{RESET}")
    print(f"   {BOLD}Заголовок:{RESET} {title}")
    print(f"   {BOLD}Текст:{RESET}     {body}\n")


DEMO_NEWS = [
    {
        "news_id": 701,
        "name": "Пример 1: Служба управления данными (СУД) + КИС УАТ + ЕППО",
        "title": "Выделение вычислительных мощностей для Службы управления данными (СУД)",
        "body": (
            "В рамках обеспечения бесперебойной работы сервисов КИС УАТ и ЕППО, "
            "а также в целях поддержания проектной деятельности на текущем уровне, "
            "для СУД были выделены дополнительные вычислительные мощности, включающие "
            "Linux-сервер с тремя ускорителями NVIDIA A100 и более чем 324 ГБ ОЗУ."
        ),
    },
    {
        "news_id": 702,
        "name": "Пример 2: ИСУНД АСУТП + КАСУА + СПИК",
        "title": "Интеграция ИСУНД АСУТП с системами КАСУА и СПИК",
        "body": (
            "Специалисты завершили интеграцию ИСУНД АСУТП с корпоративными системами "
            "КАСУА и СПИК для автоматического контроля ИТ-активов и нормативной документации."
        ),
    },
    {
        "news_id": 703,
        "name": "Пример 3: КИС ЭАД (МАДОК) и КИС Доступ",
        "title": "Модернизация архива КИС ЭАД (МАДОК)",
        "body": (
            "В корпоративной системе КИС ЭАД (МАДОК) внедрена новая подсистема фильтрации, "
            "а подача заявок на доступ переведена в КИС Доступ."
        ),
    },
]


async def main():
    header("СРАВНИТЕЛЬНОЕ ТЕСТИРОВАНИЕ РЕЖИМОВ ПЕРЕВОДА ИТ-АББРЕВИАТУР")

    print(f"{BLUE}Инициализация компонентов...{RESET}")
    from src.backend.api.schemas import TranslationRequest
    from src.backend.services.glossary_service import GlossaryService
    from src.backend.services.llm_client import create_llm_client
    from src.backend.services.translation_service import TranslationService

    glossary = GlossaryService("configs/glossary/transneft_glossary_v002.runtime.json")
    llm = create_llm_client(backend="litellm", base_url="http://localhost:8001/v1", target_model="milmmt-12b")
    service = TranslationService(glossary=glossary, llm=llm)


    print(f"{GREEN}[INFO] Загружено {len(glossary.terms)} терминов глоссария.{RESET}\n")

    for item in DEMO_NEWS:
        print(f"{BOLD}{YELLOW}{'-' * 80}{RESET}")
        print(f"{BOLD}{YELLOW}[+] {item['name']}{RESET}")
        print(f"{BOLD}{YELLOW}{'-' * 80}{RESET}")

        news_box(item["news_id"], item["title"], item["body"])

        # ПЕРЕВОД НОВОСТИ ПО КОНТРАКТУ BITBUCKET
        req = TranslationRequest(
            news_id=item["news_id"],
            title=item["title"],
            detail_text=item["body"],
        )
        t0 = time.perf_counter()
        resp = await service.translate(req)
        dt = time.perf_counter() - t0

        print(f"{GREEN}[РЕЗУЛЬТАТ ПЕРЕВОДА BITBUCKET API]:{RESET}")
        print(f"   {GREEN}news_id :{RESET} {resp.news_id}")
        print(f"   {GREEN}Title   :{RESET} {resp.translated_title}")
        print(f"   {GREEN}Detail  :{RESET} {resp.translated_detail_text}")
        print(f"   {YELLOW}Модель  :{RESET} {resp.meta.model_used} | {resp.meta.processing_time_ms} ms")
        print(f"   {BOLD}Распознанные и применённые термины:{RESET}")
        for t in resp.meta.terms_applied:
            print(f"     * [{t.term_id}] {t.ru_term} -> {BOLD}{t.en_preferred}{RESET}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
