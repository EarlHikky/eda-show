from collections import defaultdict
from json import load, dump
from os import remove

from ollama import Client
from tqdm import tqdm


def load_existing_results(filename) -> dict | defaultdict:
    """Load existing results from a file if it exists."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return load(file)
    except FileNotFoundError:
        return defaultdict(dict)


def main() -> None:
    """Main function to add recipe types to a JSON file.
    This function reads a list of recipes from a JSON file, adds the recipe type to each recipe,
    and saves the results to another JSON file.
    Raises:
        SystemExit: If the input file does not exist.
    """
    client = Client(host='http://192.168.31.13:11434')
    try:
        with open('_recipes.json', 'r', encoding='utf-8') as file:
            recipes = load(file)
    except FileNotFoundError:
        print('File _recipes.json not found. Possible, there are no new recipes.')
        exit()
    result_dict = load_existing_results('recipes.json')
    total = len(recipes)
    for key, value in tqdm(recipes.items(), desc='Processing recipes', unit='recipe', total=total):
        # Skip recipes that have already been processed
        if any(key in result for result in result_dict.values()):
            continue
        try:
            # Generate the recipe type using the Ollama API
            response = client.generate(model='ramsy', prompt=key)
            recipe_type = response.get('response')
            # Create a new dictionary with the recipe type and URL
            new_value_dict = {'type': recipe_type, 'url': value}
            # Add the new recipe to the result dictionary
            result_dict[recipe_type][key] = new_value_dict
            # Save the updated result dictionary to a JSON file
            with open('recipes.json', 'w', encoding='utf-8') as outfile:
                dump(result_dict, outfile, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f'Ошибка при обработке рецепта {key}')
            exit(str(e))
    # Remove the input file after processing
    remove('_recipes.json')


if __name__ == '__main__':
    main()
