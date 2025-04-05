import json
import redis
from config import URL
from scraper import fetch_page
from data_collector import get_numbers
from time_parsing import filter_numbers
import time
from get_messages import process_messages  # Импортируем функцию из get_messages.py

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# redis_client.flushdb() # Очистка БД


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

            # Запускаем функцию из второго скрипта для получения сообщений
            print("Запуск обработки сообщений...")
            process_messages()  # Вызываем функцию из get_messages.py

        except Exception as e:
            print(f"Ошибка: {e}")

        # Пауза на 1 час (3600 секунд)
        time.sleep(3600)

if __name__ == "__main__":
    main()
