import random
import time
from redis_client import redis_client  # Убедись, что есть подключение Redis
from config import PROXY_FILE, PROXIES_KEY, BLOCKED_KEY, BLOCK_TIME


def initialize_proxies():
    """
    Загружает прокси из файла в Redis, если ключ ещё не существует.
    """
    if not redis_client.exists(PROXIES_KEY):
        try:
            with open(PROXY_FILE) as f:
                proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                redis_client.rpush(PROXIES_KEY, *proxies)
                print(f"[init] Загружено {len(proxies)} прокси в Redis.")
        except FileNotFoundError:
            print(f"[init] Файл {PROXY_FILE} не найден. Прокси не загружены.")


def load_data():
    """
    Загружает список доступных прокси и заблокированных прокси из Redis.
    :return: (proxies: list[str], blocked: dict[str, float])
    """
    proxies = redis_client.lrange(PROXIES_KEY, 0, -1)
    proxies = [p.decode() if isinstance(p, bytes) else p for p in proxies]

    blocked_raw = redis_client.hgetall(BLOCKED_KEY)
    blocked = {
        k.decode() if isinstance(k, bytes) else k:
            float(v.decode()) if isinstance(v, bytes) else float(v)
        for k, v in blocked_raw.items()
    }
    return proxies, blocked


def block_proxy(proxy, block_time=BLOCK_TIME):
    """
    Блокирует указанный прокси на заданное время (по умолчанию 1800 сек).
    :param proxy: str
    :param block_time: int
    :return: None
    """
    expire_at = time.time() + block_time
    redis_client.hset(BLOCKED_KEY, proxy, expire_at)


def get_proxy():
    """
    Возвращает случайный незаблокированный прокси из Redis.
    :return: str | None
    """
    proxies, blocked = load_data()
    now = time.time()
    available = [p for p in proxies if blocked.get(p, 0) < now]
    return random.choice(available) if available else None


# Инициализация при первом импорте модуля
initialize_proxies()
