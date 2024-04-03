import json
import math
import sys
import os
from database import JsonData, create_session, setup_database

engine = setup_database()

file_path = sys.argv[1]
no = 0

with open(file_path, "r") as f:
    
    entries = json.load(f)
    for i in entries:
        for j in entries[i]:
            no += 1
    
            try:
                session = create_session(engine)
                json_data_obj = JsonData(entry=j)
                session.add(json_data_obj)
                session.commit()
                session.close()
                print(json.dumps({"message": "JSON data inserted successfully"}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))

    print(no)

