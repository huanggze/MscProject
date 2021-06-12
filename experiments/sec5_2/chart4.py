import matplotlib.pyplot as plt
import numpy as np

labels = ["Go", "Java", "C#\n(.Net)", "JavaScript\n(Node.js)", "PHP", "Python3"]
data = [4.929, 12.885, 5.260, 5.739, 5.473, 8.436]

x = np.array(labels)
y = np.array(data)

plt.ylabel('Time (s)')

for a,b in zip(x, y):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=9)

plt.bar(x, y, width=0.3, tick_label=labels)
plt.ylim(0, 14)
plt.show()