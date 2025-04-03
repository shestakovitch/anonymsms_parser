from config import url
from scraper import fetch_page
from data_collector import get_numbers
from time_parsing import filter_numbers
import json

def main():
    try:
        # Загрузка страницы
        soup = fetch_page(url)
        data = get_numbers(soup)  # Получаем список номеров

        # Фильтруем данные
        filtered_data = filter_numbers(data)

        # Выводим отфильтрованные данные
        print(json.dumps(filtered_data, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
