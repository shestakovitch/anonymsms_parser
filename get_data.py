import time
import json
from data_collector import process_link, get_timestamp
from redis_client import redis_client
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_data():
    """
    Обрабатывает данные, полученные из Redis:
    - Извлекает фильтрованные номера, сохраняет только те, у которых статус 'active'.
    - Для каждого активного номера вызывает функцию обработки ссылок в многозадачном режиме (пул потоков).
    - Добавляет только новые сообщения для каждого номера, сортирует их по времени и сохраняет обратно в Redis.
    Во время работы функция:
    - Проверяет наличие необходимых данных в Redis.
    - Обрабатывает ошибки, если они возникают при извлечении и обработке данных.
    - Сохраняет итоговые данные сообщений в Redis для дальнейшего использования.
    :return: None
    """
    print("Запуск обработки данных...")
    raw = redis_client.get("filtered_numbers")
    if not raw:
        print("Данные в Redis не найдены.")
        return

    filtered = json.loads(raw)
    links = [
        num["link"]
        for country_data in filtered
        for country_info in country_data.values()
        for num in country_info["numbers"]
        if num.get("status") == "active"
    ]
    print(f"Найдено активных номеров: {len(links)}")
    if not links:
        return

    messages_data = json.loads(redis_client.get("messages_data") or "{}")

    # Собираем мапу номера -> страна
    number_country = {
        number["phone_number"].lstrip("+"): country
        for entry in filtered
        for country, data in entry.items()
        for number in data["numbers"]
        if number.get("status") == "active"
    }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_link, link) for link in links]
        for future in as_completed(futures):
            try:
                number_id, new_msgs = future.result()
                country = number_country.get(number_id, "unknown")

                messages_data.setdefault(country, {})
                old_msgs = messages_data[country].get(number_id, [])

                known = {(m["from"], m["text"]) for m in old_msgs if m.get("from") and m.get("text")}
                unique = [m for m in new_msgs if (m.get("from"), m.get("text")) not in known]

                sorted_new = sorted(unique, key=get_timestamp)
                messages_data[country][number_id] = sorted_new

            except Exception as e:
                print(f"Ошибка: {e}")

    print(json.dumps(messages_data, indent=4, ensure_ascii=False))
    redis_client.set("messages_data", json.dumps(messages_data, ensure_ascii=False, indent=2))
    print("Сообщения успешно сохранены в Redis.\n")


def process_messages():
    """
    Запускает бесконечный цикл обработки данных каждую минуту:
    - Каждый цикл вызывает функцию обработки данных process_data.
    - После обработки данных делает паузу на 60 секунд перед следующим циклом.
    :return: None
    """
    while True:
        process_data()
        time.sleep(60)
