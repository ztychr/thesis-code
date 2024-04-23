import json
import sqlite3
import sys
import matplotlib.pyplot as plt
from datetime import datetime

connection = sqlite3.connect(sys.argv[1])
cursor = connection.cursor()

try:
    cursor.execute("SELECT * FROM json_data")
    rows = cursor.fetchall()

    timestamps = []
    values = []

    for row in rows:
        json_row = json.loads(row[1])

        if json_row["group"] == sys.argv[2]: 
        # Extract timestamp
            timestamp_str = json_row["data"]["timestamp"]
            timestamp = datetime.fromtimestamp(float(timestamp_str))
        
            timestamps.append(timestamp)
            values.append(1)  # Example value for demonstration, you can use actual data here

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, values, 'bo', markersize=8)  # 'bo' represents blue circle marker
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Time Series Plot')
    plt.grid(True)
    plt.show()

except sqlite3.Error as e:
    print(f"Error reading data: {e}")

finally:
    connection.close()
