import requests
from redis_client import redis_client

phone = "447464143355"

url = "https://dev.7sim.cc/in"
params_add_number = {
    "token": "sd232hasasdS",
    "action": "newnum",
    "phone": phone,
    "country_code": "US",
    "site": f"https://anonymsms.com/number/{phone}/"
}

params_send_sms = {
    "token": "sd232hasasdS",
    "action": "newsms",
    "phone": phone,
    "from": "TEST",
    "message": "Follow the white rabbit",
    "site": f"https://anonymsms.com/number/{phone}/"
}


response_add_number = requests.get(url=url, params=params_add_number)
# print(response_add_number.status_code)
# print(response_add_number.text)

response_send_sms = requests.get(url=url, params=params_send_sms)
print(response_send_sms.status_code)
print(response_send_sms.text)