import json
import sqlite3
import sys
from datetime import datetime, timedelta

connection = sqlite3.connect(sys.argv[1])
cursor = connection.cursor()

try:
    group_names = sys.argv[2:]
    
    hourly_counts = {group_name: {hour: 0 for hour in range(24)} for group_name in group_names}
    total_hourly_counts = {hour: 0 for hour in range(24)}
    four_hour_interval_counts = {hour: 0 for hour in range(24)}
    
    cursor.execute("SELECT * FROM json_data")
    rows = cursor.fetchall()
    
    for row in rows:
        json_row = json.loads(row[1])
        group_name = json_row["group"]
        
        if group_name in group_names:
            timestamp_str = json_row["data"]["timestamp"]
            timestamp = datetime.fromtimestamp(float(timestamp_str))
            
            hourly_counts[group_name][timestamp.hour] += 1
            total_hourly_counts[timestamp.hour] += 1
    
    interval_start = 7
    interval_end = 11
    
    interval_count = 0
    for hour in range(interval_start, interval_end):
        interval_count += total_hourly_counts[hour % 24]
    
    for group_name in group_names:
        print(f"Group: {group_name}")
        for hour, count in hourly_counts[group_name].items():
            print(f"Hour {hour}:00 - {hour + 1}:00: {count} scans")
        print()
    
    print("Combined Count for Each Hour:")
    for hour in range(24):
        combined_count = sum(hourly_counts[group_name][hour] for group_name in group_names)
        print(f"Hour {hour}:00 - {hour + 1}:00: {combined_count} scans")
    
    print(f"\nTotal Count for {interval_start}:00 - {interval_end}:00 Interval:", interval_count)
    
except IndexError:
    print("Usage: python script.py <database_file> <group_name1> <group_name2> ...")
