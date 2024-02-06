import json
import sqlite3
import sys


def print_database_contents(database_path, group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    amount = 0

    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()
        print("ID | JSON Line")

        for row in rows:
            json_dict = json.loads(row[1])
            if json_dict["group"] == group:
                amount += 1
                print(f"{row[0]} |", json_dict)

    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()
        print("total", amount)


database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
