import matplotlib.pyplot as plt

plt.subplots_adjust(left=0, bottom=0.2, right=0.8, top=0.8)

ax = plt.subplot(111)  # 创建一个1x1网格中的第一个子图
ax.plot([1, 2, 3], [4, 5, 6])

plt.show()