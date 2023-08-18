import json
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup


def pages_count(session):
    url = 'https://eda.show/tag/recipe/'
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    pages = int(soup.find('div', class_='pagination-wrapper').text.split()[-1])
    return pages


def scrape_page(page, session, recipes):
    url = f'https://eda.show/tag/recipe/page/{page}'
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    recipe_tags = soup.find_all('div', class_='col l6 m6 s12')
    for recipe_tag in recipe_tags:
        recipe_name = recipe_tag.find('div', class_='card-limiter').h3.text
        recipe_url = f'https://eda.show/{recipe_tag.a["href"].strip("/")}'
        recipes[recipe_name] = recipe_url


def main():
    recipes = dict()
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda p: scrape_page(p, session, recipes), range(1, pages_count(session) + 1))

    with open('recipes4.json', 'w') as file:
        json.dump(recipes, file)


if __name__ == '__main__':
    main()
