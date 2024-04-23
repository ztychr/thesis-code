import json
import sqlite3
import sys

def update_database_group(database_path, group, new_group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()

        for row in rows:
            jd = json.loads(row[1])
            if jd.get("group") == group:
                jd["group"] = new_group
                updated_json = json.dumps(jd)
                cursor.execute("UPDATE json_data SET entry = ? WHERE id = ?", (updated_json, row[0]))
        
        connection.commit()  # Commit the transaction
        print("Group updated successfully.")

    except sqlite3.Error as e:
        print("Error updating group:", e)

    finally:
        connection.close()  # Close the database connection


# Usage example:
database_path = sys.argv[1]
group = sys.argv[2]
new_group = sys.argv[3]
update_database_group(database_path, group, new_group)
