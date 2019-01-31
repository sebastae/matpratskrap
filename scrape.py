import codecs
import json
import os

import sys

import bs4
import requests
import sqlite3


def scrape(name: str):
    data_path = f"{os.path.dirname(sys.argv[0])}/data"

    urls = get_sub_urls(name)

    """Write urls to file"""
    f = open(f"{data_path}/{name}_urls.txt", 'a')
    f.writelines(map(lambda s: f"{s}\r", urls))
    f.close()

    recipes = []
    ingredients_all = []

    """Scrape and add each recipe to recipe list"""
    counter = 1
    for url in urls:
        if not url == "":
            print(f"GET {url} : {counter} / {len(urls)}")
            counter += 1
            response = requests.get(f"https://www.matprat.no/{url}")
            soup = bs4.BeautifulSoup(response.text, features="html.parser")

            title_element = soup.find("h1")
            title = title_element.text

            ingredient_list = soup.find_all("li", attrs={'itemprop':'ingredients'})
            ingredients = []

            """Extract ingredients"""
            for ingredient in ingredient_list:
                amount_tag = ingredient.find("span", class_="amount")
                unit_tag = ingredient.find("span", class_="unit")
                amount = amount_tag['data-amount']
                unit = unit_tag['data-unit']

                try:
                    ingredient_name = list(filter(bool, map(lambda s: s.strip().replace("\n"," "), ingredient.text.split("\r\n"))))[-1]
                except IndexError as e:
                    print(e)
                    ingredient_name = "??"
                ingredients.append({'amount': amount, 'unit': unit, 'name': ingredient_name})

                """If we haven't encountered the ingredient previously, add it to a "global" list of ingredients """
                if ingredient_name not in ingredients_all:
                    ingredients_all.append(ingredient_name)

            recipe = {'name': title,
                      'url': url,
                      'ingredients': ingredients}

            recipes.append(recipe)

    try:
        conn = sqlite3.connect(f"{data_path}/{name}.db")
        cursor = conn.cursor()
        """Add ingredients to db"""
        for i in range(len(ingredients_all)):
            # print("Inserting " + ingredients_all[i])
            cursor.execute(f"INSERT INTO Ingredient (ID, Name) VALUES ({i},'{ingredients_all[i]}')")

        for i in range(len(recipes)):
            print(f"Inserting recipe {recipes[1].get('name')}")
            cursor.execute("INSERT INTO Recipe (ID, Name, Url) VALUES (?,?,?)", (i, recipes[i].get('name'), recipes[i].get('url')))
            for ingredient in recipes[i].get('ingredients'):
                ing_index = ingredients_all.index(ingredient.get('name'))
                # print(f"Inserting relation {recipes[i].get('name')} - {ingredients_all[ing_index]}")
                try:
                    cursor.execute(f"INSERT INTO RecipeIngredient (RecipeID, IngredientID, Unit, Amount) "
                                   f"VALUES (?,?,?,?)", (i, ing_index, ingredient.get('unit'), ingredient.get('amount')))
                except sqlite3.Error as e:
                    print(e)
    except sqlite3.Error as e:
        print(e)
    finally:
        cursor.close()
        conn.commit()
        conn.close()



def get_sub_urls(name: str):
    """Find all recipe-urls from main search page"""
    urls = []

    page_counter = 1
    recipe_counter = 0
    """Loop until no more results"""
    while(True):
        url = f"https://www.matprat.no/api/Search/GetSearchResults?page={page_counter}&type=recipe&searchFor="

        response = requests.get(url)
        data = json.loads(response.content)

        hits = data.get("SearchHits")

        """Exit loop if no more results are found"""
        if len(hits) == 0:
            break
        page_counter += 1

        """Write all recipe urls to file"""
        for hit in hits:
            urls.append(hit.get('Url'))
            recipe_counter += 1
            print(f"Found '{hit.get('Name')}': {hit.get('Url')}")

    print(f"Found {recipe_counter} over {page_counter-1} pages")
    return urls



