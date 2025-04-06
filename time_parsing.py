import re


def text_to_seconds(time_in_text):
    """
    # Функция для преобразования времени из текста в секунды
    :param time_in_text:
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