from concurrent.futures import ThreadPoolExecutor
from json import dump, load
from os import path

from bs4 import BeautifulSoup
from requests import Session, Response
from tqdm import tqdm

STATE_FILE = 'scraping_state.json'


def load_state():
    """Load the last processed page from the state file."""
    if path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            state = load(file)
        return state.get('last_page', 0)
    return 0


def save_state(last_page):
    """Save the last processed page to the state file."""
    state = {'last_page': last_page}
    with open(STATE_FILE, 'w') as file:
       dump(state, file)


def pages_count(session: Session) -> int:
    """Count the number of pages."""
    url = 'https://eda.show/tag/recipe/'
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    pages = int(soup.find('div', class_='pagination-wrapper').text.split()[-1])
    return pages


def scrape_page(page: int, session: Session, recipes: dict[str, str]) -> None:
    """Get the URLs of the recipes on the given page."""
    url = f'https://eda.show/tag/recipe/page/{page}'
    response: Response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    recipe_tags = soup.find_all('div', class_='col l6 m6 s12')
    for recipe_tag in recipe_tags:
        recipe_name: str = recipe_tag.find('div', class_='card-limiter').h3.text
        recipe_url = f'https://eda.show/{recipe_tag.a["href"].strip("/")}'
        recipes[recipe_name] = recipe_url


def main():
    """
    Main function that scrapes recipes from eda.show and saves them to a JSON file.
    """
    recipes = dict()  # Dictionary to store the scraped recipes

    with Session() as session:
        total_pages = pages_count(session)  # Get the total number of pages
        last_page = load_state()  # Load the last processed page from the state file

        if last_page == total_pages:  # Check if all pages have been processed
            print('No new recipes')
            exit()

        last_page = total_pages - last_page + 1  # Calculate the number of pages to scrape

        with ThreadPoolExecutor(max_workers=10) as executor:
            pages_to_scrape = range(1, last_page)  # Get the pages to scrape
            total = len(pages_to_scrape)  # Get the total number of pages to scrape

            # Submit tasks to the executor and store the future objects in a dictionary
            future_to_page = {executor.submit(scrape_page, page, session, recipes): page for page in pages_to_scrape}

            # Process the futures and wait for them to complete
            for future in tqdm(future_to_page, total=total, desc="Processing ...", unit="page", leave=False):
                future.result()

        save_state(total_pages)  # Save the pages count to the state file

    with open('_recipes.json', 'w') as file:
        dump(recipes, file, ensure_ascii=False, indent=4)  # Save the recipes to a JSON file


if __name__ == '__main__':
    main()
