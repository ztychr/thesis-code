import json
import sqlite3
import sys


def print_database_contents(database_path, group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    data = {}
    amount = 0
    
    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()

        for row in rows:
            jd = json.loads(row[1])
            if jd.get("group") == group:
                if jd.get("filename") == "qr" or jd.get("src") == "qr":
                    amount += 1


    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()
        data["qr"] = amount
                
    print(json.dumps(data, indent=2))


database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
