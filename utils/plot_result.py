import sys, json, math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

file_path = sys.argv[1]
group = sys.argv[1].split(".")[0]
timestamps = []

with open(file_path, "r") as f:
    list = json.load(f)
    entries = list[group]

    for entry in entries:
        ts = int(entry["data"]["timestamp"].split(".")[0])
        timestamps.append(ts)
    #    print(strftime('%Y-%m-%d %H:%M:%S', localtime(i)))
    datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
    elapsed_time = [(dt - datetimes[0]).total_seconds() for dt in datetimes]
    y_values = range(1, len(datetimes) + 1)

    plt.plot(datetimes, y_values, marker="o")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title("Time vs QR")
    plt.margins(x=0.05)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
    plt.yticks(range(math.ceil(min(y_values)), math.floor(max(y_values)) + 1))
    plt.xticks(rotation=45)
    for x, y in zip(datetimes, y_values):
        adjusted_y = y  # + 0.1
        if y < 4:
            adjusted_x = x + timedelta(seconds=600)
            ha = "left"
        else:
            adjusted_x = x - timedelta(seconds=600)
            ja = "right"
        ha = "left" if y < 4 else "right"
        plt.text(
            adjusted_x, adjusted_y, x.strftime("%H:%M"), ha=ha, va="center"
        )  # rotation=45)
    plt.show()
