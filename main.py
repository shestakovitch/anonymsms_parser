import json
import threading
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
    - В бесконечном цикле загружает страницу, получает данные и сохраняет их в Redis.
    - Добавляет временную метку последнего обновления.
    - Запускает фоновую обработку сообщений с использованием внешней функции process_messages.

    В процессе работы:
    - Загружает HTML-страницу с номерами телефонов с сайта BASE_URL.
    - Извлекает список стран и номеров с помощью функции get_numbers().
    - Сохраняет полученные данные в Redis под ключом "filtered_numbers".
    - Записывает текущую временную метку в Redis под ключом "activity_detection_time".
    - Запускает функцию process_messages в отдельном потоке, чтобы не блокировать основной цикл.
    - В случае возникновения исключения выводит сообщение об ошибке.
    - После завершения каждого цикла делает паузу на 1 час (3600 секунд) перед следующей итерацией.

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

            # Запускаем фоновую обработку сообщений
            threading.Thread(target=process_messages, daemon=True).start()
            print("Фоновая обработка сообщений запущена.\n")

        except Exception as e:
            print(f"Ошибка: {e}")

        # Пауза на 1 час (3600 секунд)
        time.sleep(3600)


if __name__ == "__main__":
    main()
