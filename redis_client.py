import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD

# Подключение к Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)
