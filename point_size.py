import numpy as np
from scipy.interpolate import interp1d

x = np.array([100, 90, 80, 70, 60, 50, 40, 30, 20, 15, 10, 5])
y = np.array([1, 1.04, 1.11, 1.19, 1.26, 1.34, 1.42, 1.51, 1.59, 1.63, 1.67, 1.72])


def CalPointSize(pointNum) :
    # 创建线性插值函数对象
    linear_func = interp1d(x, y, kind='linear')
    adjustParam = linear_func(pointNum)

    pointLen = (20.5 * 10)/pointNum
    return pointLen * pointLen * adjustParam
