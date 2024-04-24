import json
import sqlite3
import sys


def print_database_contents(database_path, group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    ids = {}
    types = {}
    
    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()

        for row in rows:
            jd = json.loads(row[1])
            if jd.get("group") == group:
                fn = jd.get("filename")
                idx = jd.get("id")
                typex = jd.get("typex")

                

                try:
                    if jd.get("src") == "qr":
                        continue
                    if idx in ids and idx in types:
                        ids[idx].append(fn)
                    else:
                        ids[idx] = []
                        types[idx] = typex
                        ids[idx].append(fn)
                                                                
                except Exception as e:
                    print(e)
 
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()
        print(json.dumps(types, indent=2))
        print(json.dumps(ids, indent=2))



database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
