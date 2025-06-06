import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
SMS_URL = os.getenv("SMS_URL")
SMS_TOKEN = os.getenv("SMS_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

PROXY_FILE = "proxies.txt"
PROXIES_KEY = "proxies"
BLOCKED_KEY = "blocked_proxies"
BLOCK_TIME=1800 # Время на которое прокси исключается из обхода в случае блокировки.