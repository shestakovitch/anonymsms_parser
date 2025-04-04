import requests
from bs4 import BeautifulSoup
import fake_user_agent
from random_proxy import get_proxy, block_proxy


def fetch_page(url):
    """
    Отправляет GET-запрос по указанному URL и возвращает объект BeautifulSoup.
    """
    user = fake_user_agent.user_agent()
    headers = {'User-Agent': user}

    while True:
        proxy = get_proxy()
        if not proxy:
            raise Exception("Нет доступных прокси.")

        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            return BeautifulSoup(response.text, "lxml")

        except requests.RequestException as e:
            print(f"Ошибка с прокси {proxy}: {e}. Блокируем и пробуем другой.")
            block_proxy(proxy)
