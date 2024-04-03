import json
import sqlite3
import sys


def print_database_contents(database_path, group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    amount = 0
    files = {}
    sticks = {}
    data = {}
    ids = []
    
    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()

        for row in rows:
            jd = json.loads(row[1])
            if jd.get("group") == group:
                fn = jd.get("filename")
                sticktype = jd.get("typex")
                print(jd, "\n\n")

                try:
                    if jd.get("src") == "qr":
                        continue
                    if jd.get("whois", {}).get("isp") != "Microsoft Corporation":
                        if not jd.get("id") in ids:
                            ids.append(jd["id"])
                            sticks[sticktype] = sticks.get(sticktype, 0) + 1
                        files[fn] = files.get(fn, 0) + 1
                        amount+=1
                                                                
                except Exception as e:
                    files[fn] = files.get(fn, 0) + 1
                    sticks[sticktype] = sticks.get(sticktype, 0) + 1
                    amount += 1
                    if not jd["id"] in ids:
                        ids.append(jd["id"])
                        sticks[sticktype] = sticks.get(sticktype, 0) + 1


        sticks["total"] = len(ids)
        files["total"] = amount

#        print(f"{row[0]} |", jd)

    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()
        print("total files", amount)
        print("total sticks", len(ids))

        data["files"] = files
        data["sticks"] = sticks
        print(json.dumps(data, indent=2))


database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
