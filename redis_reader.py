from redis_client import redis_client

# Подключаемся к Redis


# Получаем все ключи в базе данных
# key_message_data_new = redis_client.keys('messages_data_new')
keys = redis_client.keys('*')

# Для каждого ключа выводим его значение
for key in keys:
    value = redis_client.get(key)
    print(f"{key}: {value}")


# Очистка БД
# redis_client.flushdb()