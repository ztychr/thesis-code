import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch

def grouped_column_plot(data, device_data):
    versions = sorted(data.keys())
    num_versions = len(versions)
    
    labels = ["low", "medium", "high", "critical"]
    num_vars = len(labels)

    bar_width = 0.15
    index = np.arange(num_versions)
    colors = {'low': '#c8e071', 'medium': '#ffdb69', 'high': '#ff8e58', 'critical': '#ff182b'}
    handles = []

    fig, ax1 = plt.subplots()

    for i, label in enumerate(labels):
        stats = [data[version][label] for version in versions]
        bars = ax1.bar(index + i * bar_width, stats, bar_width, label=label, color=colors[label])
        handles.append(bars[0])
    
    count_stats = [device_data[version]["count"] for version in versions]
    ax1.plot(index + bar_width * (num_vars - 1) / 2, count_stats, marker='o', linestyle='-', color='black', label=f'Number of Devices (Total: {data2["count"]})')
    
    ax1.set_xlabel('Safari Versions')
    ax1.set_ylabel('Number of Vulnerabilities')
    ax1.set_title('DTU: Counts of Safari Versions, Vulnerabilities and Severities')
    ax1.set_xticks(index + bar_width * (num_vars - 1) / 2)
    ax1.set_xticklabels(versions)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    #ax1.yaxis.set_label_coords(-0.1, 0.5)
    #ax1.set_ylim(0, 3.5)

    handles = [art for art in handles if not art.get_label().startswith('_')]
    
    # legend
    legend_elements = [Patch(facecolor=color, edgecolor='black', label=label) for label, color in colors.items()]
    ax1.legend(handles=handles + legend_elements + [ax1.lines[-1]], loc='upper center', bbox_to_anchor=(0.5, 1))
    
    # debuuuug
    for art in handles:
        if art.get_label().startswith('_'):
            print("Artist label starting with underscore:", art.get_label())

grouped_column_plot(data1, data2)

plt.show()
