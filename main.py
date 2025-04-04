import json
import redis
from config import URL
from scraper import fetch_page
from data_collector import get_numbers
from time_parsing import filter_numbers
import time

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def main():
    while True:
        try:
            print("Загружаем страницу")
            soup = fetch_page(URL)

            print("Получаем список стран и номеров")
            data = get_numbers(soup)

            print("Фильтруем данные")
            filtered_data = filter_numbers(data)

            # Сохраняем в Redis
            redis_client.set("filtered_numbers", json.dumps(filtered_data, ensure_ascii=False))

            print("Данные сохранены в Redis!")

        except Exception as e:
            print(f"Ошибка: {e}")

        # Пауза на 1 час (3600 секунд)
        time.sleep(3600)  # Пауза 1 час


if __name__ == "__main__":
    main()
