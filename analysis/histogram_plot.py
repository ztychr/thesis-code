import json
import sqlite3
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DayLocator, DateFormatter, HourLocator, AutoDateLocator
import matplotlib.ticker as ticker

connection = sqlite3.connect(sys.argv[1])
cursor = connection.cursor()

try:
    group_names = sys.argv[2:]
    
    for group_name in group_names:
        
        timestamps = []
        
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()
        
        for row in rows:
            json_row = json.loads(row[1])
            if json_row["group"] == group_name:
                if json_row["src"] == "qr": # for 1 and 2
                #if json_row["filename"] == "qr": # for 3 and 4

                # Extract timestamp
                    timestamp_str = json_row["data"]["timestamp"]
                    timestamp = datetime.fromtimestamp(float(timestamp_str))
                    if float(timestamp_str) < 1708038001:
                        timestamps.append(timestamp)
                        
                # Plot histogram
        plt.hist(timestamps, bins=30, alpha=0.7, label=f'QR Code Scans (Total: {len(timestamps)})', linewidth=6)

    # Get the minimum and maximum dates to determine the date range
    min_date = min(timestamps)
    max_date = max(timestamps)
    
    # Calculate the number of hours between min_date and max_date
    num_days = (max_date - min_date).days
    num_hours = int((max_date - min_date).total_seconds() / 3600)
    
    # Calculate the middle of each hour and create ticks
    # middle of each day
    #ticks = [min_date + timedelta(days=i + 0.5) for i in range(num_days)]
    #ticks = [min_date + timedelta(hours=i + 0.5) for i in range(num_hours)]
    
    # Set the ticks and format the x-axis
    #plt.xticks(ticks, [tick.strftime('%Y-%m-%d %H:%M') for tick in ticks])
    # Set the ticks and format the x-axis
    #plt.xticks(ticks, [tick.strftime('%Y-%m-%d') for tick in ticks])


    #plt.ylim(0, 4)
    
    plt.xlabel('Date')
    plt.ylabel('Frequency')
    plt.title('UFM: Histogram of Timestamps')
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align to the right
    plt.subplots_adjust(bottom=0.2)  # Increase space at the bottom for labels


#    plt.gca().xaxis.set_major_locator(HourLocator(byhour=range(0, 24, 8)))
#    plt.gca().xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))  # Format as year-month-day hour:minute

    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(base=1))
    # Set the locator and formatter for x-axis
    plt.gca().xaxis.set_major_locator(AutoDateLocator())
    
    #plt.gca().xaxis.set_major_locator(DayLocator())
    plt.gca().xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))  # Format as year-month-day
    
    plt.legend()
    plt.show()

except IndexError:
    print("Usage: python script.py <database_file> <group_name1> <group_name2> ...")
