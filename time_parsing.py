import re


def text_to_seconds(time_in_text):
    """
    # Функция для преобразования времени из текста в секунды
    :param latest:
    :return:
    """
    match = re.match(r"(\d+) (\w+) ago", time_in_text)
    if not match:
        return float('inf')  # Если не удалось распарсить, считаем как неактивный

    value, unit = int(match.group(1)), match.group(2).lower().rstrip('s')  # Убираем 's' на конце

    conversion = {
        "second": 1, "minute": 60, "hour": 3600,
        "day": 86400, "week": 604800, "month": 2592000, "year": 31536000
    }

    return value * conversion.get(unit, float('inf'))


def filter_numbers(all_data):
    """
    Фильтрует номера по активности
    :param all_data: список словарей с данными по странам
    :return: список стран с разделением номеров на активные/неактивные
    """
    filtered_data = []

    for country_data in all_data:
        country = country_data["country"]
        numbers = country_data["numbers"]

        active_numbers = [num for num in numbers if text_to_seconds(num["latest"]) <= 120]
        inactive_numbers = [num for num in numbers if text_to_seconds(num["latest"]) > 120]

        filtered_data.append({
            "country": country,
            "active_numbers": active_numbers,
            "inactive_numbers": inactive_numbers
        })

    return filtered_data
