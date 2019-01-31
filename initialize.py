import os
import sqlite3

import sys


def create_file(fn: str):
    """Create empty file, overwrites old file if exists"""
    print(f"Creating new file '{fn}'")
    open(fn, "w").close()


def create_db(fn: str):
    """Create empty SQLite database"""
    print(f"Creating new SQLite database '{fn}'")
    try:
        conn = sqlite3.connect(fn)
        print("Successfully connected to SQLite database")
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()
        print("Connection closed")

def init_db(fn: str):

    try:
        conn = sqlite3.connect(fn)

        """Drop relevant tables"""
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS Recipe")
        cursor.execute("DROP TABLE IF EXISTS Ingredient")
        cursor.execute("DROP TABLE IF EXISTS RecipeIngredient")
        cursor.close()

        """Create tables again"""
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE Recipe(ID INTEGER, Name TEXT, Url TEXT, PRIMARY KEY (ID))")
        cursor.execute("CREATE TABLE Ingredient(ID INTEGER, Name TEXT, PRIMARY KEY (ID))")
        cursor.execute("CREATE TABLE RecipeIngredient(RecipeID INTEGER, IngredientID INTEGER, Unit TEXT, Amount INTEGER, PRIMARY KEY (RecipeID, IngredientID))")
        cursor.close()

        conn.commit()

    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()


def init(name: str):
    current_dir = os.path.dirname(sys.argv[0])
    db_path = f"{current_dir}/data/{name}.db"
    list_path = f"{current_dir}/data/{name}_urls.txt"

    """Make sure data directory exists"""
    if not os.path.exists(f"{current_dir}/data"):
        os.makedirs(f"{current_dir}/data")
        print("Created new data directory")

    create_db(db_path)
    init_db(db_path)
    create_file(list_path)

    print("Initialization done")



