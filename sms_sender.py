import requests
from config import SMS_TOKEN

url = "https://dev.7sim.cc/in"

data = {
    "united-kingdom": {
        "447919744718": [
            {
                "from": "SIGNAL",
                "text": "SIGNAL: Your code is: 097669 Do not share this code",
                "date": "4 Minutes ago",
                "checked_at": "23:08:14 09-04-2025"
            },
            {
                "from": "+12792101203",
                "text": "Wer Earning [ coint.top ] Userme: Mik e68 PasIN: E v0618 Balance:* 8 ,491 ,759 ,92",
                "date": "3 Minutes ago",
                "checked_at": "23:08:14 09-04-2025"
            },
            {
                "from": "SIGNAL",
                "text": "SIGNAL: Your code is: 814228 Do not share this code doDiFGKP O1 r",
                "date": "1 Minute ago",
                "checked_at": "23:08:14 09-04-2025"
            }
        ]
    }
}


def send_request(action, params, description):
    try:
        response = requests.get(url, params=params, timeout=10)
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
    if not SMS_TOKEN:
        print("Ошибка: переменная окружения SMS_TOKEN не установлена.")
        return

    for country, numbers in data.items():
        for phone, messages in numbers.items():
            site = f"https://anonymsms.com/number/{phone}/"

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


# Запуск
send_sms(data)
