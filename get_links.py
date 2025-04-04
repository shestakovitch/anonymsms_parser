import redis
import json
from scraper import fetch_page
from data_collector import get_messages

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
data = redis_client.get("filtered_numbers")  # Получаем данные
if data:
    filtered_data = json.loads(data)
    print("Данные загружены!")
else:
    print("Данные не найдены в Redis")
    exit()

active_numbers_links = [num["link"] for country_data in filtered_data for num in country_data["active_numbers"]]
inactive_numbers_links = [num["link"] for country_data in filtered_data for num in country_data["inactive_numbers"]]

# print(active_numbers_links)
messages_data = {}
for link in active_numbers_links:
    soup = fetch_page(link)
    messages_data[link] = get_messages(soup)

print(json.dumps(messages_data, indent=4, ensure_ascii=False))