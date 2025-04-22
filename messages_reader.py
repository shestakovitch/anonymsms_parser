from redis_client import redis_client

# Подключаемся к Redis


# Ключи связанным с сообщениями
keys = ('activity_detection_time', 'filtered_numbers', "messages_data_old", "messages_data_new")

# Для каждого ключа выводим его значение
for key in keys:
    value = redis_client.get(key)
    print(f"{key}: {value}")
