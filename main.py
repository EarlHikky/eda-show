import time
import json
import requests
from bs4 import BeautifulSoup

recipes = dict()
for page in range(1, 150):
    url = f'https://eda.show/tag/recipe/page/{page}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    recipes_tag = soup.find('div', class_='wrapper')
    recipes_rows_tags = recipes_tag.find_all('div', class_='row')
    for row in recipes_rows_tags:
        for recipe_tag in row.find_all('div', class_='col l6 m6 s12'):
            recipe_name = recipe_tag.find('div', class_='card-limiter').h3.text
            recipe_url = f"https://eda.show/{recipe_tag.a['href'].strip('/')}"
            recipes.setdefault(recipe_name, recipe_url)
    # time.sleep(1)

with open('reciepes.json', 'w') as file:
    json.dump(recipes, file)






