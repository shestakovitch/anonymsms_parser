import json
import time
from datetime import datetime
from config import BASE_URL
from scraper import fetch_page
from data_collector import get_numbers
from get_data import process_messages
from redis_client import redis_client


def main():
    """
    Главная функция для выполнения следующих шагов:
    - Очищает базу данных Redis.
    - В бесконечном цикле загружает страницу, получает данные и сохраняет их в Redis.
    - Запускает обработку сообщений с использованием внешней функции process_messages из другого скрипта.
    В процессе работы:
    - Скачивает страницу с номерами, извлекает необходимые данные, и сохраняет их в Redis.
    - Дополнительно сохраняет временную метку начала сбора данных в Redis под ключом "last_updated".
    - Запускает функцию обработки сообщений, которая будет обновлять информацию о номерах.
    - В случае ошибки выводит сообщение об ошибке.
    - После выполнения каждого цикла делает паузу на 1 час перед повторной загрузкой данных.
    :return: None
    """

    while True:
        try:
            print("Загружаем страницу")
            soup = fetch_page(BASE_URL)

            print("Получаем список стран и номеров")
            data = get_numbers(soup)

            # Сохраняем данные в Redis
            redis_client.set("filtered_numbers", json.dumps(data, ensure_ascii=False))

            # Добавляем timestamp обновления
            timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            redis_client.set("activity_detection_time", timestamp)

            print("Данные и время последнего обновления сохранены в Redis!")
            print("Запуск обработки сообщений...")
            process_messages()

        except Exception as e:
            print(f"Ошибка: {e}")

        # Пауза на 1 час (3600 секунд)
        time.sleep(3600)


if __name__ == "__main__":
    main()
