from config import url
from scraper import fetch_page
from data_collector import get_numbers
# from time_parsing import parse_time


def main():
    try:
        # Загрузка страницы
        soup = fetch_page(url)
        print(get_numbers(soup))


    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
