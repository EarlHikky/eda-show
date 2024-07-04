from argparse import ArgumentParser
from json import load
from random import choice


def get_random_recipe(recipe_type: str = None) -> tuple:
    """
    Choose a random recipe from the 'recipes.json' file.

    Args:
        recipe_type (str, optional): The type of recipe to choose from. If not provided, a random recipe type is chosen.

    Returns:
        tuple: A tuple containing the name of the chosen recipe and its URL.
    """
    # Open the 'recipes.json' file and load its contents into a dictionary
    with open('recipes.json', 'r') as file:
        recipes = load(file)

    # If no recipe type is provided, choose a random recipe type from the dictionary keys
    if recipe_type is None:
        recipe_type = choice(list(recipes.keys()))

    # Choose a random recipe from the chosen recipe type's dictionary items
    random_choice = choice(list(recipes[recipe_type].items()))

    # Print the recipe name and URL
    # print(random_choice[0], random_choice[1]['url'], sep='\n')

    # Return the chosen recipe as a tuple
    return random_choice


def main(recipe_type: str = None) -> None:
    """
    Main function to get a random recipe.
    Args:
        recipe_type (str, optional): Recipe type. Defaults to None.
    Returns:
        None
    """
    if recipe_type is None:
        # Create argument parser
        parser = ArgumentParser(
            description='Get one random recipe'
        )
        # Add argument for recipe type
        parser.add_argument(
            '-r',
            help='recipe type in (Breakfast, Lunch, Dinner, Supper, Dessert, Snack)'
        )
        # Parse arguments
        args = parser.parse_args()
        # Get recipe type from arguments
        recipe_type = args.r
        # Get random recipe
    get_random_recipe(recipe_type)


if __name__ == '__main__':
    main()
