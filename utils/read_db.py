import json
import sqlite3
import sys


def print_database_contents(database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()
        print("ID | JSON Line")

        for row in rows:
            json_dict = json.loads(row[1])
            if json_dict["group"] == "ufm":
                print(f"{row[0]} |", json_dict)

    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()


database_path = sys.argv[1]
print_database_contents(database_path)
