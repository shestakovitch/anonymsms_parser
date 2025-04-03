import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

data = redis_client.get("filtered_numbers")  # Получаем данные
if data:
    filtered_data = json.loads(data)
    print("Данные загружены!")
else:
    print("Данные не найдены в Redis")
    exit()

links_to_scrape = []
for country_data in filtered_data:
    for num in country_data["active_numbers"]:
        links_to_scrape.append(num["link"])  # Берем ссылку

print(links_to_scrape)