import time
import redis
import json
from data_collector import get_messages, process_link, get_timestamp
from concurrent.futures import ThreadPoolExecutor, as_completed

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def process_data():
    print("Запуск обработки данных...")
    raw = redis_client.get("filtered_numbers")
    if not raw:
        print("Данные в Redis не найдены.")
        return

    filtered = json.loads(raw)
    links = [num["link"] for c in filtered for num in c if num.get("status") == "active"]
    print(f"Найдено активных номеров: {len(links)}")
    if not links:
        return

    messages_data = json.loads(redis_client.get("messages_data") or "{}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        for future in as_completed([executor.submit(process_link, link) for link in links]):
            try:
                number_id, new_msgs = future.result()
                old_msgs = messages_data.get(number_id, [])

                known = {(m["from"], m["text"]) for m in old_msgs if m.get("from") and m.get("text")}
                unique_new = [m for m in new_msgs if (m.get("from"), m.get("text")) not in known]

                combined = old_msgs + unique_new
                combined.sort(key=get_timestamp)
                messages_data[number_id] = combined
            except Exception as e:
                print(f"Ошибка: {e}")

    print(json.dumps(messages_data, indent=4, ensure_ascii=False))
    redis_client.set("messages_data", json.dumps(messages_data, ensure_ascii=False, indent=2))
    print("Сообщения успешно сохранены в Redis.\n")


def process_messages():
    while True:
        process_data()
        time.sleep(60)
