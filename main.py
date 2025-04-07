import os
import json
import redis
import time
from dotenv import load_dotenv
from config import BASE_URL
from scraper import fetch_page
from data_collector import get_numbers
from get_data import process_messages

# Загружаем переменные окружения
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Подключение к Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Очистка БД
redis_client.flushdb()


def main():
    while True:
        try:
            print("Загружаем страницу")
            soup = fetch_page(BASE_URL)

            print("Получаем список стран и номеров")
            data = get_numbers(soup)

            # Сохраняем в Redis
            redis_client.set("filtered_numbers", json.dumps(data, ensure_ascii=False))
            print("Данные сохранены в Redis!")

            # Запускаем функцию из второго скрипта для получения сообщений
            print("Запуск обработки сообщений...")
            process_messages()  # Вызываем функцию из get_data.py

        except Exception as e:
            print(f"Ошибка: {e}")

        # Пауза на 1 час (3600 секунд)
        time.sleep(3600)


if __name__ == "__main__":
    main()
