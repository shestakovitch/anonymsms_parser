import time
import redis
import json
from datetime import datetime, timedelta
from scraper import fetch_page
from data_collector import get_messages
from time_parsing import text_to_seconds
from concurrent.futures import ThreadPoolExecutor, as_completed

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def process_link(link):
    soup = fetch_page(link)
    messages = get_messages(soup)

    timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    for message in messages:
        message['checked_at'] = timestamp

    number_id = link.rstrip('/').split('/')[-1]
    return number_id, messages


def process_data():
    print("Запуск обработки данных...")
    data = redis_client.get("filtered_numbers")
    if data:
        filtered_data = json.loads(data)
        print("Загружены данные из Redis.")
    else:
        print("Данные в Redis не найдены.")
        return

    active_numbers_links = [
        num["link"]
        for country_data in filtered_data
        for num in country_data
        if num.get("status") == "active"
    ]

    print(f"Найдено активных номеров: {len(active_numbers_links)}")
    if not active_numbers_links:
        print("Активные номера отсутствуют.")
        return

    messages_data = {}
    existing_raw = redis_client.get("messages_data")
    if existing_raw:
        messages_data = json.loads(existing_raw)
        print("Загружены ранее сохранённые сообщения.")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_link, link) for link in active_numbers_links]

        for future in as_completed(futures):
            try:
                number_id, new_messages = future.result()
                existing_messages = messages_data.get(number_id, [])

                existing_set = {
                    (m.get("from"), m.get("text"))
                    for m in existing_messages
                    if m.get("from") and m.get("text")
                }

                new_unique = [
                    m for m in new_messages
                    if m.get("from") and m.get("text") and (m["from"], m["text"]) not in existing_set
                ]

                combined = existing_messages + new_unique

                # Сортировка по возрасту сообщения (от старого к новому)
                def get_message_timestamp(message):
                    """
                    Возвращает точное время получения сообщения как datetime, на основе date и checked_at
                    """
                    date_text = message.get("date", "9999 years ago")
                    checked_at_str = message.get("checked_at")

                    try:
                        checked_at = datetime.strptime(checked_at_str, "%H:%M:%S %d-%m-%Y")
                        seconds_ago = text_to_seconds(date_text)
                        return checked_at - timedelta(seconds=seconds_ago)
                    except Exception:
                        return datetime.min  # для некорректных значений — ставим в начало

                combined = existing_messages + new_unique
                combined.sort(key=get_message_timestamp)
                messages_data[number_id] = combined

            except Exception as e:
                print(f"Ошибка при обработке номера: {e}")

    print(json.dumps(messages_data, indent=4, ensure_ascii=False))
    redis_client.set("messages_data", json.dumps(messages_data, ensure_ascii=False, indent=2))
    print("Сообщения успешно сохранены в Redis.\n")


def process_messages():
    while True:
        process_data()
        time.sleep(60)
