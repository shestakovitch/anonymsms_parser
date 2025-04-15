import requests
from config import BASE_URL, SMS_TOKEN, SMS_URL
from logger_config import setup_logger

logger = setup_logger("sms_sender", "sms.log")


def send_request(action, params, description):
    """
    Отправляет GET-запрос к API SMS-сервиса.
    """
    try:
        response = requests.get(SMS_URL, params=params, timeout=10)
        response.raise_for_status()
        logger.info(f"[OK] {description} | Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 'No status')
        response_text = getattr(e.response, 'text', 'No body')
        logger.error(f"[HTTP ERROR] {description} | Status: {status_code} | {e}")
        logger.error(f"Response: {response_text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"[REQUEST ERROR] {description} | {e}")
    except Exception as e:
        logger.error(f"[UNEXPECTED ERROR] {description} | {e}", exc_info=True)


def send_sms(data):
    """
    Отправляет SMS-сообщения через внешний сервис.
    """
    if not SMS_TOKEN:
        logger.error("Ошибка: переменная окружения SMS_TOKEN не установлена.")
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
                }, f"SMS от '{message['from']}' -> {phone} | Сообщение: {message['text']}")
