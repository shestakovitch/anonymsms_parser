import time

import redis
import json
from scraper import fetch_page
from data_collector import get_messages
from concurrent.futures import ThreadPoolExecutor, as_completed

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Функция для извлечения сообщений с одной страницы
def process_link(link):
    soup = fetch_page(link)
    messages = get_messages(soup)
    return link.rstrip('/').split('/')[-1], messages

# Многопоточная обработка
def process_data():
    # Получаем данные из Redis
    data = redis_client.get("filtered_numbers")
    if data:
        filtered_data = json.loads(data)
        print("Загружены данные из Redis!")
    else:
        print("Данные не найдены в Redis")
        return

    # Извлекаем ссылки на активные и неактивные номера
    active_numbers_links = [num["link"] for country_data in filtered_data for num in country_data["active_numbers"]]

    messages_data = {}

    # Используем пул потоков для обработки активных номеров
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_link, link) for link in active_numbers_links]

        # Собираем результаты по мере завершения задач
        for future in as_completed(futures):
            try:
                link, messages = future.result()
                messages_data[link] = messages
            except Exception as e:
                print(f"Ошибка при обработке ссылки {link}: {e}")

    # Выводим полученные сообщения
    print(json.dumps(messages_data, indent=4, ensure_ascii=False))

# Главная функция для запуска обработки сообщений
def process_messages():
    while True:
        process_data()
        time.sleep(60)
