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
    :param soup:
    :return:
    """
    countries_list = get_countries(soup)
    # return countries_list
    for country in countries_list:
        # print(country)
        soup = fetch_page(url=url + country)
        data = {"country": country,
                "numbers": [
            {
                "link": card.select_one('.sms-card__number a')['href'],
                "phone_number": card.select_one('.sms-card__number a').get_text(strip=True),
                "latest": card.select_one('.sms-card__item:-soup-contains("schedule") .text--bold').get_text(strip=True)
            }
            for card in soup.select('.sms-card')
        ]
        }

        for k, v in data.items():
            print(f"{k}: {v}")
