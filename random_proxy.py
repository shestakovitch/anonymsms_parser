import random
import time
import json
from config import PROXY_FILE, BLOCKED_FILE


def load_data():
    """Загружает список прокси и заблокированные прокси из файлов."""
    try:
        with open(PROXY_FILE) as file:
            proxies = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        proxies = []

    try:
        with open(BLOCKED_FILE) as file:
            blocked = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        blocked = {}

    return proxies, blocked


proxies, blocked_proxies = load_data()


def block_proxy(proxy, block_time=1800):
    """Блокирует прокси на 30 минут и сохраняет в файл."""
    blocked_proxies[proxy] = time.time() + block_time
    with open(BLOCKED_FILE, "w") as file:
        json.dump(blocked_proxies, file)


def get_proxy():
    """Возвращает случайный незаблокированный прокси."""
    available_proxies = [p for p in proxies if time.time() > blocked_proxies.get(p, 0)]
    return random.choice(available_proxies) if available_proxies else None
