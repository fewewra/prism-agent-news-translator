"""Демонстрационный скрипт локального перевода новостей с глоссарием через MiLMMT 12B."""

import asyncio
import time
from src.backend.services.llm_client import LocalMLXClient
from src.backend.api.schemas import GlossaryMode, TranslationRequest
from src.backend.services.glossary_service import GlossaryService
from src.backend.services.translation_service import TranslationService


async def main():
    print("=" * 70)
    print("1. Инициализация глоссария (pymorphy3 + transneft_glossary_v002)...")
    glossary = GlossaryService("configs/glossary/transneft_glossary_v002.runtime.json")
    print(f"   Загружено {len(glossary.terms)} терминов.")

    print("\n2. Загрузка локальной модели MiLMMT 12B в MLX (Apple Silicon)...")
    start_load = time.perf_counter()
    llm = LocalMLXClient("models/milmmt")
    print(f"   Модель загружена за {time.perf_counter() - start_load:.2f} сек.")

    service = TranslationService(glossary=glossary, llm=llm)

    request = TranslationRequest(
        title="Завод ПАО «Транснефть» разработал электродвигатель для ледокола",
        body=(
            "АО «Транснефть - Верхняя Волга» завершило плановые ремонтные работы "
            "на линейной производственно-диспетчерской станции. В ходе работ была "
            "проведена проверка запорной арматуры и подпорных насосных агрегатов, "
            "а также мероприятия по повышению экологической безопасности и охраны труда."
        ),
        glossary_mode=GlossaryMode.RETRIEVED_TOP3,
    )

    print("\n3. Входящий русский текст:")
    print(f"   Заголовок: {request.title}")
    print(f"   Текст: {request.body}")
    print(f"   Режим глоссария: {request.glossary_mode.value}")

    print("\n4. Выполнение перевода...")
    response = await service.translate(request)

    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТ ПЕРЕВОДА:")
    print(f"Title [EN]: {response.title_translated}")
    print(f"Body [EN] : {response.body_translated}")
    print(f"\nМодель: {response.model_name}")
    print(f"Время обработки: {response.processing_time_sec} сек")
    print("\nПрименённые термины глоссария:")
    for term in response.glossary_terms_applied:
        print(f"  - [{term.term_id}] {term.ru_term} → {term.en_preferred}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
