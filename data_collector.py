from bs4 import BeautifulSoup
from scraper import fetch_page
from config import URL
from time_parsing import text_to_seconds


def get_countries(soup: BeautifulSoup) -> list:
    """
    Функция получает названия стран с главной страницы
    :param soup: BeautifulSoup object
    :return list:
    """
    # Ищем тег <h2> с нужным классом и текстом "Countries", убирая лишние пробелы
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
    Функция получает список номеров со ссылками и с данными о последнем обновлении
    для всех стран.

    :param soup: BeautifulSoup object
    :return: list of dictionaries with country data
    """
    countries_list = get_countries(soup)
    data = []  # Храним данные всех стран

    for country in countries_list:
        soup = fetch_page(url=URL + country)
        country_data = {
            "country": country,
            "numbers": [
                {
                    "link": card.select_one('.sms-card__number a')['href'],
                    "phone_number": card.select_one('.sms-card__number a').get_text(strip=True),
                    "latest": card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold').get_text(
                        strip=True)
                }
                for card in soup.select('.sms-card')
            ]
        }
        data.append(country_data)

    return data


def get_messages(soup: BeautifulSoup):
    """
    Функция получает информацию о сообщениях активных номеров
    :param soup: BeautifulSoup object
    :return: list of dictionaries with country data
    """
    messages = []
    paginator = soup.select_one("div.pagination a.page-numbers")
    # print(paginator.get_text(strip=True))
    for row in soup.select("tbody tr"):
        from_td = row.select_one("td:nth-of-type(1)")
        text_td = row.select_one("td:nth-of-type(2)")
        date_td = row.select_one("td:nth-of-type(3)")
        if not (from_td and text_td and date_td) or text_to_seconds(date_td.get_text(strip=True)) > 300:
            continue  # Пропускаем строки, где нет нужных данных
        messages.append({
            "from": from_td.get_text(strip=True),
            "text": text_td.get_text(" ", strip=True),
            "date": date_td.get_text(strip=True)
        })

    return messages