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
    loc = {}
    uas = {}
    ids = []
    
    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()

        for row in rows:
            jd = json.loads(row[1])
            if jd.get("group") == group:
                fn = jd.get("filename")
                sticktype = jd.get("typex")
                location = jd.get("loc")
                #ua = jd.get("data", {}).get("User-Agent")
                
                ua = jd.get("data", {}).get("User-Agent") if jd.get("data", {}).get("User-Agent") != None else ""
                
#                print(jd, "\n\n")

                try:
                    if jd.get("src") == "qr":
                        continue
                    if jd.get("whois", {}).get("isp") != "Microsoft Corporation":
                        files[fn] = files.get(fn, 0) + 1
                        loc[location] = loc.get(location, 0) + 1
                        uas[ua] = uas.get(ua, 0) + 1
                        if not jd.get("id") in ids:
                            ids.append(jd["id"])
                            sticks[sticktype] = sticks.get(sticktype, 0) + 1
                        
                        
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

    except sqlite3.Error as e:
        print(f"Error reading data: {e}")

    finally:
        connection.close()

        data["files"] = files
        data["sticks"] = sticks
        data["location"] = loc
        data["user-agents"] = uas
                
        print(json.dumps(data, indent=2))


database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
