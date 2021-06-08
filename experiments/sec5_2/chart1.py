import matplotlib.pyplot as plt
import numpy as np

labels = ["10", "20", "30", "40", "50"]
data = [41.897, 50.204, 55.879, 64.310, 55.507]

x = np.array(labels)
y = np.array(data)

plt.xlabel('Cluster Size')
plt.ylabel('Time (ms)')

for a,b in zip(x, y):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=9)

plt.bar(x, y, width=0.3, tick_label=labels)
plt.ylim(0, 70)
plt.show()