from bs4 import BeautifulSoup
from scraper import fetch_page
from config import url


def get_countries(soup: BeautifulSoup) -> list:
    """
    Функция получает названия стран с главной страницы
    :param soup:
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
        soup = fetch_page(url=url + country)
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
