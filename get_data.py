import time
import json
from data_collector import process_link, get_timestamp
from redis_client import redis_client
from concurrent.futures import ThreadPoolExecutor, as_completed
from sms_sender import send_sms

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

    # Извлекаем данные о фильтрованных номерах из Redis
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

    # Получаем старые сообщения из Redis, если они есть
    messages_data_old_raw = redis_client.get("messages_data_old")
    if messages_data_old_raw:
        messages_data_old = json.loads(messages_data_old_raw)
        print("Старые сообщения успешно извлечены.")
    else:
        messages_data_old = {}
        print("Не найдено старых сообщений в Redis, инициализируем пустой словарь.")

    messages_data_new = {}

    # Собираем мапу номера -> страна
    number_country = {
        number["phone_number"].lstrip("+"): country
        for entry in filtered
        for country, data in entry.items()
        for number in data["numbers"]
        if number.get("status") == "active"
    }

    print("Обработка сообщений для активных номеров...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_link, link) for link in links]
        for future in as_completed(futures):
            try:
                number_id, new_msgs = future.result()
                country = number_country.get(number_id, "unknown")

                # Инициализируем данные для нового списка сообщений, если они ещё не инициализированы
                messages_data_new.setdefault(country, {})
                old_msgs = messages_data_old.get(country, {}).get(number_id, [])

                # Множество старых сообщений (from, text) для быстрого поиска
                known = {(m["from"], m["text"]) for m in old_msgs if m.get("from") and m.get("text")}

                # Фильтруем только новые сообщения, которых нет в известных
                unique = [m for m in new_msgs if (m.get("from"), m.get("text")) not in known]

                # Если есть новые сообщения, добавляем их в список
                if unique:
                    sorted_new = sorted(unique, key=get_timestamp)
                    messages_data_new[country][number_id] = sorted_new
                else:
                    # Если новых сообщений нет, оставляем пустым
                    messages_data_new[country][number_id] = []

            except Exception as e:
                print(f"Ошибка: {e}")

    # Объединяем старые и новые данные
    for country, numbers in messages_data_new.items():
        if country not in messages_data_old:
            messages_data_old[country] = {}

        for number_id, new_msgs in numbers.items():
            # Объединяем старые и новые сообщения для каждого номера
            existing_msgs = messages_data_old[country].get(number_id, [])
            updated_msgs = existing_msgs + new_msgs
            messages_data_old[country][number_id] = updated_msgs

    # Сохраняем обновлённые данные (старые + новые) в Redis
    print("Сохранение объединённых данных в Redis...")
    print(json.dumps(messages_data_new, indent=4, ensure_ascii=False))

    # Сохраняем объединённые данные (старые + новые) в Redis
    redis_client.set("messages_data_old", json.dumps(messages_data_old, ensure_ascii=False, indent=2))

    # Сохраняем новые сообщения в Redis для проверки работы парсера
    redis_client.set("messages_data_new", json.dumps(messages_data_new, ensure_ascii=False, indent=2))
    print("Сообщения успешно сохранены в Redis.\n")

    return messages_data_new

def process_messages():
    """
    Запускает бесконечный цикл обработки данных каждую минуту:
    - Каждый цикл вызывает функцию обработки данных process_data.
    - После обработки данных делает паузу на 60 секунд перед следующим циклом.
    :return: None
    """
    while True:
        messages_data = process_data()
        send_sms(messages_data)
        print("Ожидание 60 секунд перед следующим циклом...")
        time.sleep(60)
