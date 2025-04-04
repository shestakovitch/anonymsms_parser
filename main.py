import json
import redis
from config import URL
from scraper import fetch_page
from data_collector import get_numbers
from time_parsing import filter_numbers

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def main():
    try:
        # Загрузка страницы
        soup = fetch_page(URL)
        # Получаем список номеров
        data = get_numbers(soup)

        # Фильтруем данные
        filtered_data = filter_numbers(data)

        # Сохраняем в Redis
        redis_client.set("filtered_numbers", json.dumps(filtered_data, ensure_ascii=False))

        print("Данные сохранены в Redis!")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
