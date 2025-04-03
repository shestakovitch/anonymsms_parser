# import json
# import re
# from data_collector import   # Импортируем данные из файла data_collector.py
#
# # Функция для преобразования времени в секунды
# def parse_time(latest):
#     match = re.match(r"(\d+) (\w+) ago", latest)
#     if not match:
#         return float('inf')  # Если не удалось распарсить, считаем как неактивный
#
#     value, unit = int(match.group(1)), match.group(2).lower().rstrip('s')  # Убираем 's' на конце
#
#     conversion = {
#         "second": 1, "minute": 60, "hour": 3600,
#         "day": 86400, "week": 604800, "month": 2592000, "year": 31536000
#     }
#
#     return value * conversion.get(unit, float('inf'))
#
# # Пример использования данных из data_collector.py
# country = data["country"]
# numbers = data["numbers"]
#
# # Разделение на активные и неактивные
# active_numbers = [num for num in numbers if parse_time(num["latest"]) <= 120]
# inactive_numbers = [num for num in numbers if parse_time(num["latest"]) > 120]
#
# result = {
#     "country": country,
#     "active_numbers": active_numbers,
#     "inactive_numbers": inactive_numbers
# }
#
# print(json.dumps(result, indent=4, ensure_ascii=False))