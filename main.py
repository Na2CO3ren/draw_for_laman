# import sys
# new_path = '/Users/bytedance/Library/Python/3.9/bin'
# sys.path.append(new_path)
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from fontTools.misc.cython import returns

import page_show as show
import data_import as data
import const.const as const
import threshold as thd

# matplotlib.use('TkAgg')
matplotlib.rcParams['figure.dpi'] = 150

# substanceName = show.ShowSubstanceInput()

substance = data.ImportData(const.ShowSubstanceName)

# 设置图片参数
ScatterFig, ScatterAxs = plt.subplots()
ScatterFig.set_size_inches(4.9, 4.9)
ScatterFig.patch.set_visible(False)
ScatterFig.set_frameon(False)

show.DrawScatter(substance, ScatterFig, ScatterAxs)


# TODO:
#  2、支持调节阈值的时候动态的选择多样颜色
