import requests
from config import BASE_URL, SMS_TOKEN, SMS_URL


def send_request(action, params, description):
    """
    Отправляет GET-запрос к API SMS-сервиса.
    - Использует URL, указанный в конфигурации (SMS_URL).
    - Передаёт параметры запроса, включая токен, действие и дополнительные данные.
    - Выводит статус ответа и текст ответа в консоль.
    - В случае ошибок выводит подробную информацию об ошибке:
        - HTTP-ошибки (например, 400, 403, 500 и т.д.).
        - Ошибки соединения и таймаутов.
        - Любые непредвиденные исключения.
    :param action: Тип действия (например, "newnum" или "newsms").
    :param params: Словарь параметров запроса.
    :param description: Описание действия, отображаемое в логах.
    :return: None
    """
    try:
        response = requests.get(SMS_URL, params=params, timeout=10)
        response.raise_for_status()
        print(f"[OK] {description} | Status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP ERROR] {description} | {e} | Response: {getattr(e.response, 'text', 'No body')}")
    except requests.exceptions.RequestException as e:
        print(f"[REQUEST ERROR] {description} | {e}")
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {description} | {e}")


def send_sms(data):
    """
    Отправляет SMS-сообщения через внешний сервис.
    - Проверяет наличие токена авторизации (SMS_TOKEN), необходимого для API-запросов.
    - Проходит по всем странам и номерам в словаре `data`.
    - Сначала отправляет запрос на добавление номера (`action=newnum`).
    - Затем для каждого сообщения по номеру отправляет запрос на отправку SMS (`action=newsms`).
    - Каждый запрос сопровождается логированием результата (успех/ошибка).
    Пример структуры входных данных:
    {
        "united-kingdom": {
            "447919744718": [
                {"from": "SIGNAL", "text": "Your code is 1234"},
                ...
            ]
        }
    }
    :param data: Словарь с номерами телефонов и сообщениями по странам.
    :return: None
    """
    if not SMS_TOKEN:
        print("Ошибка: переменная окружения SMS_TOKEN не установлена.")
        return

    for country, numbers in data.items():
        for phone, messages in numbers.items():
            site = f"{BASE_URL}/number/{phone}/"

            # Добавляем номер
            send_request("newnum", {
                "token": SMS_TOKEN,
                "action": "newnum",
                "phone": phone,
                "country_code": country,
                "site": site
            }, f"Добавление номера {phone} ({country})")

            # Отправляем SMS
            for message in messages:
                send_request("newsms", {
                    "token": SMS_TOKEN,
                    "action": "newsms",
                    "phone": phone,
                    "from": message['from'],
                    "message": message['text'],
                    "site": site
                }, f"SMS от '{message['from']}' -> {phone}")
