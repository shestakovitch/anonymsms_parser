import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

data = redis_client.get("filtered_numbers")  # Получаем данные
if data:
    print(json.loads(data))  # Декодируем из JSON и печатаем
else:
    print("Данных нет в Redis!")