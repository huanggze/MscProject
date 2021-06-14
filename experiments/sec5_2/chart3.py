import matplotlib.pyplot as plt
import numpy as np

labels = ["cilium", "flannel", "calico", "weave", "kube-router"]
data1 = [0.563, 0.137, 0.335, 0.285, 0.122]
data2 = [1.850, 1.466, 1.625, 1.515, 1.339]

x = np.array(labels)
y1 = np.array(data1)
y2 = np.array(data2)

plt.subplot(211)
for a,b in zip(x, y1):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=8)
plt.ylabel('Time (s)')
plt.ylim(0, 0.6)
plt.bar(x, y1, width=0.3)

plt.subplot(212)
for a,b in zip(x, y2):
    plt.text(a, b, b, ha='center', va='bottom', fontsize=8)
plt.ylabel('Time (s)')
plt.ylim(0, 2)
plt.bar(x, y2, width=0.3, tick_label=labels)

plt.show()