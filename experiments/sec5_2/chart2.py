import matplotlib.pyplot as plt
import numpy as np

labels = ["Docker", "containerd", "CRI-O"]
data = [1.856, 1.632, 1.559]

x = np.array(labels)
y = np.array(data)

plt.ylabel('Time (seconds)')

for a,b in zip(x, y):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=9)

plt.bar(x, y, width=0.3, tick_label=labels)
plt.ylim(0, 2)
plt.show()