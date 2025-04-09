from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from scraper import fetch_page
from config import BASE_URL
from time_parsing import text_to_seconds


def get_countries(soup: BeautifulSoup) -> list:
    """
    Получает список стран с главной страницы сайта.

    Алгоритм:
    1. Находит заголовок <h2> с классом "category-group__title title title--underlined"
       и текстом "Countries" (без учёта лишних пробелов).
    2. Если заголовок найден — ищет следующий <div> с классом "category-group__btn-group", который содержит ссылки на страны.
    3. Извлекает текст из каждой ссылки <a>, приводит к нижнему регистру и заменяет пробелы на дефисы.

    Пример возвращаемого списка:
        ['united-states', 'russia', 'germany', ...]

    :param soup: Объект BeautifulSoup главной страницы
    :return: Список названий стран в формате, подходящем для подстановки в URL
    """
    h2_tag = soup.find("h2", class_="category-group__title title title--underlined",
                       string=lambda text: text and text.strip() == "Countries")
    if not h2_tag:
        print("Countries section not found")
        return []

    # Возвращаем список стран
    return [a.get_text(strip=True).lower().replace(" ", "-")
            for a in h2_tag.find_next("div", class_="category-group__btn-group").find_all("a")]


def get_numbers(soup: BeautifulSoup):
    """
    Извлекает список телефонных номеров с дополнительной информацией для каждой страны.
    Функция выполняет следующее:
    1. Получает список всех стран с помощью функции `get_countries`.
    2. Для каждой страны делает запрос к соответствующей странице.
    3. Извлекает данные для каждого телефонного номера, включая:
       - Ссылку на страницу с сообщениями
       - Сам номер телефона
       - Время последнего обновления сообщений ("latest")
       - Время добавления номера ("added")
       - Статус номера: "active", если последнее сообщение было не старше 2 часов (7200 секунд), иначе — "inactive"
    4. Сохраняет текущий timestamp в Redis.
    5. Возвращает список всех стран с их активными/неактивными номерами и сопутствующими данными.

    :param soup: Объект BeautifulSoup главной страницы
    :return: Список списков словарей — по одной вложенной записи (стране) на каждый набор номеров.
    """
    countries_list = get_countries(soup)
    data = []  # Храним данные всех стран

    for country in countries_list:
        soup = fetch_page(url=BASE_URL + country)
        country_data = {country:
            {"numbers": [{
                "link": card.select_one('.sms-card__number a')['href'],
                "phone_number": card.select_one('.sms-card__number a').get_text(strip=True),
                "latest": (
                    card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold')
                    .get_text(strip=True)
                    if card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold') else None
                ),
                "added": (
                    card.select_one('.sms-card__item:-soup-contains("add_circle") .text--bold')
                    .get_text(strip=True)
                    if card.select_one('.sms-card__item:-soup-contains("add_circle") .text--bold') else None
                ),
                "status": (
                    "active"
                    if card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold')
                       and text_to_seconds(
                        card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold').get_text(
                            strip=True)) <= 7200
                    else "inactive"
                )
            }
                for card in soup.select('.sms-card')
            ]
            }
        }
        if country_data:
            data.append(country_data)

    return data


def get_messages(soup: BeautifulSoup):
    """
    Извлекает сообщения из HTML-таблицы, представленной объектом BeautifulSoup.

    Фильтрует только те сообщения, которые были получены за последние 5 минут (300 секунд),
    основываясь на тексте в колонке с датой.

    :param soup: Объект BeautifulSoup, содержащий HTML-страницу со списком сообщений
    :return: Список словарей, каждый из которых содержит поля:
             - 'from': номер отправителя
             - 'text': текст сообщения
             - 'date': строка с возрастом сообщения (например, "2 Minutes ago")
    """
    messages = []
    for row in soup.select("tbody tr"):
        from_td = row.select_one("td:nth-of-type(1)")
        text_td = row.select_one("td:nth-of-type(2)")
        date_td = row.select_one("td:nth-of-type(3)")
        if not (from_td and text_td and date_td) or text_to_seconds(date_td.get_text(strip=True)) > 300:
            continue  # Пропускаем строки, где нет нужных данных
        messages.append({
            "from": from_td.get_text(strip=True),
            "text": text_td.get_text(separator=" ", strip=True),
            "date": date_td.get_text(strip=True)
        })

    return messages


def get_timestamp(msg):
    """
    Вычисляет точное время получения сообщения на основе двух полей:
    - 'checked_at': время, когда сообщение было проверено (в формате "%H:%M:%S %d-%m-%Y")
    - 'date': относительное время, например "2 minutes ago"
    Функция вычитает количество секунд, указанных в поле 'date', из времени 'checked_at',
    чтобы получить точное время поступления сообщения.
    Если формат данных некорректный или возникает ошибка при разборе, возвращается минимальное значение времени (datetime.min),
    чтобы такие сообщения оказались в начале при сортировке.
    :param msg: словарь с данными сообщения
    :return: объект datetime с точным временем поступления сообщения
    """
    try:
        checked = datetime.strptime(msg.get("checked_at", ""), "%H:%M:%S %d-%m-%Y")
        seconds_ago = text_to_seconds(msg.get("date", "9999 years ago"))
        return checked - timedelta(seconds=seconds_ago)
    except:
        return datetime.min


def process_link(link):
    """
    Обрабатывает ссылку на номер телефона:
    - Загружает HTML-страницу по ссылке с помощью fetch_page.
    - Извлекает список сообщений с этой страницы с помощью get_messages.
    - Добавляет каждому сообщению поле 'checked_at' с текущим временем,
      чтобы в дальнейшем можно было точно рассчитать время получения сообщения.
    - Возвращает:
        - ID номера (извлечённый из конца ссылки),
        - список сообщений.
    :param link: URL-адрес страницы номера телефона
    :return: кортеж (number_id, messages)
    """
    soup = fetch_page(link)
    messages = get_messages(soup)
    now = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    for msg in messages:
        msg['checked_at'] = now
    return link.rstrip('/').split('/')[-1], messages
