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

# pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
# 找id要找这个              const elementId = '{{ plot_div.split("<div id=\\"")[1].split("\\"")[0] }}'


# matplotlib.use('TkAgg')
matplotlib.rcParams['figure.dpi'] = 150
plt.rcParams['font.family'] = 'Hiragino Sans GB'  # 使用黑体字体，可根据系统情况替换为其他支持中文的字体
plt.rcParams['axes.unicode_minus'] = False

# substanceName = show.ShowSubstanceInput()

substance = data.ImportData(const.ShowSubstanceName)
jsonify({
        'curve_data':substance.curves[0]
    })

# 设置图片参数
# ScatterFig, (ScatterAxs, linAxs) = plt.subplots(1,2)
# plt.subplots_adjust(left=0, bottom=0.2, right=0.8, top=0.8)
# ScatterFig.set_size_inches(4.9*2 +2, 4.9)
ScatterFig, ScatterAxs = plt.subplots()
ScatterFig.set_size_inches(4.9, 4.9)
ScatterFig.patch.set_visible(False)
ScatterFig.set_frameon(False)

show.DrawScatter(substance, ScatterFig, ScatterAxs)


# TODO:
#  2、支持调节阈值的时候动态的选择多样颜色
