import requests
from bs4 import BeautifulSoup
import fake_user_agent
from random_proxy import get_proxy, block_proxy


def fetch_page(url):
    """
    Загружает HTML-страницу с указанного URL с использованием случайного User-Agent и прокси.

    Основные шаги выполнения:
    - Генерирует случайный User-Agent с помощью библиотеки fake_user_agent.
    - В бесконечном цикле:
        - Получает новый прокси с помощью функции get_proxy.
        - Формирует словарь прокси для передачи в запросе.
        - Выполняет GET-запрос с указанным URL, прокси и заголовками.
        - При успешном ответе возвращает объект BeautifulSoup для парсинга HTML.
        - В случае возникновения ошибки (например, таймаут, отказ соединения, блокировка):
            - Выводит сообщение об ошибке.
            - Блокирует текущий прокси через функцию block_proxy.
            - Продолжает цикл с новым прокси.
    - Если список прокси исчерпан, выбрасывает исключение.

    Особенности:
    - Используется таймаут 5 секунд, чтобы ускорить повторные попытки при сбоях.
    - Поддерживается как HTTP-, так и HTTPS-прокси.
    - Используется lxml-парсер для быстрой и корректной обработки HTML.

    :param url: URL-адрес страницы, которую нужно загрузить.
    :return: Объект BeautifulSoup с HTML-содержимым страницы.
    :raises Exception: Если ни один из прокси не сработал.
    """
    user = fake_user_agent.user_agent()
    headers = {'User-Agent': user}

    while True:
        proxy = get_proxy()
        if not proxy:
            raise Exception("Нет доступных прокси.")

        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            return BeautifulSoup(response.text, "lxml")

        except requests.RequestException as e:
            print(f"Ошибка с прокси {proxy}: {e}. Блокируем и пробуем другой.")
            block_proxy(proxy)
