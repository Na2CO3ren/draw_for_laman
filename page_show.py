import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector
import model.model as model
import threshold as thd
import util.util as util
import const.const as const
import data_import as data
import point_size as point_size
import const.color as color

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QFormLayout,QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import sys

current_curve_fig = None

# 绘制散点图
def DrawScatter(substance,ScatterFig, ScatterAxs):

    # 提取坐标点的x坐标和y坐标
    locaX = np.array([point.locaX for point in substance.points])
    locaY = np.array([point.locaY for point in substance.points])

    # 获取颜色数组
    colors = [const.ShowColorMap.get(point.color) for point in substance.points]
    # 计算散点大小
    size = point_size.CalPointSize(substance.pointXNum)
    # 绘制散点图
    scatter_plot = ScatterAxs.scatter(locaX, locaY, c=colors, s=size, picker=True, marker="s")
    xMin, xMax = CalScatterXRange(substance.points)
    ScatterAxs.set_xlim(xMin,xMax)
    yMin, yMax = CalScatterYRange(substance.points)
    ScatterAxs.set_ylim(yMin,yMax)


    # # 设置坐标轴标签和标题
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Intensity')

    # 定义点击事件处理函数
    def on_pick(event):
        if event.artist == scatter_plot:
            # 获取被点击点的索引
            ind = event.ind[0]
            print(f"Clicked point coordinates: ({locaX[ind]}, {locaY[ind]})")
            # 获取曲线信息
            curve = substance.curves[ind]
            a = drawInnerLine(substance, locaX[ind], locaY[ind], ind, curve, ScatterFig, ScatterAxs)

    # 连接点击事件和处理函数
    cid = ScatterFig.canvas.mpl_connect('pick_event', on_pick)

    # 显示图形
    plt.show()


# 弹出阈值输入框
def ShowThresholdInput(x, y):
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("阈值输入")

    layout = QFormLayout()
    layout.setLabelAlignment(Qt.AlignLeft)

    # 前两行展示包含变量x的文本
    layout.addRow("xMin:", QLabel(f'{x}'))
    layout.addRow("xMax:", QLabel(f'{y}'))

    # 第三行创建可输入的文本框
    threshold_edit = QLineEdit()
    layout.addRow("threshold input:", threshold_edit)

    # 第四行和第五行创建颜色下拉列表
    comboBox1 = QComboBox()
    comboBox1.addItems(color.MainPointColor)
    layout.addRow("color type:", comboBox1)
    comboBox2 = QComboBox()
    comboBox2.addItems(color.SubColorMap[color.MainPointColor[0]])
    layout.addRow("sub color type:", comboBox2)
    displayLabel = QLabel('         ')
    layout.addRow("display color:", displayLabel)


    def comboBox1ChangeEvent():
        selectedOption = comboBox1.currentText()
        comboBox2.clear()
        comboBox2.addItems(color.SubColorMap[selectedOption])
    # 动态关联
    comboBox1.currentIndexChanged.connect(comboBox1ChangeEvent)

    def comboBox2ChangeEvent():
        selectedOption = comboBox2.currentText()
        color = QColor(selectedOption)
        palette = displayLabel.palette()
        palette.setColor(QPalette.Background, color)
        displayLabel.setPalette(palette)
        displayLabel.setAutoFillBackground(True)
    comboBox2ChangeEvent() #先调用一次
    comboBox2.currentIndexChanged.connect(comboBox2ChangeEvent)


    def get_result():
        result = threshold_edit.text()
        window.close()
        app.quit()
        return result

    submit_button = QPushButton("提交")
    submit_button.clicked.connect(get_result)
    layout.addWidget(submit_button)

    window.setLayout(layout)
    window.show()
    app.exec_()
    return threshold_edit.text()

# 弹出物质输入框
def ShowSubstanceInput():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("物质输入")

    layout = QVBoxLayout()

    label = QLabel("请输入想要查看的物质")
    layout.addWidget(label)

    # 第三行创建可输入的文本框
    substanceInput = QLineEdit()
    # substanceInput.setPlaceholderText("请在这里输入物质")
    layout.addWidget(substanceInput)


    def get_result():
        result = substanceInput.text()
        window.close()
        app.quit()
        # QApplication.quit()
        return result

    submit_button = QPushButton("提交")
    submit_button.clicked.connect(get_result)
    layout.addWidget(submit_button)

    window.setLayout(layout)
    window.show()
    app.exec_()
    # window.close()
    # app.quit()
    return substanceInput.text()

# 绘制曲线图
def drawInnerLine(substance,locatX,locatY, locaInd,curve,fig, axs):
    global current_curve_fig
    # 绘制曲线
    new_fig, new_ax = plt.subplots()
    current_curve_fig = new_fig
    line = new_ax.plot(curve.x, curve.y,linewidth=0.5)

    # 填充标记区间
    for lineFill in curve.lineFillList:
        if np.all(np.array(lineFill.rangeY) < lineFill.threshold):
            new_ax.fill_between(np.array(lineFill.rangeX), np.array(lineFill.rangeY), y2=lineFill.threshold,
                                where=(np.array(lineFill.rangeY) < lineFill.threshold), color='g', alpha=1)
        else:
            new_ax.fill_between(np.array(lineFill.rangeX), np.array(lineFill.rangeY), y2=lineFill.threshold,
                                where=(np.array(lineFill.rangeY) > lineFill.threshold), color='r', alpha=1)

    cfgId = util.GenCfgId(substance, locaInd)
    def onselect(xmin, xmax):
        new_x = [x_value for index, x_value in enumerate(curve.x) if xmin <= x_value <= xmax]
        new_y = [curve.y[index] for index, x_value in enumerate(curve.x) if xmin <= x_value <= xmax]
        # 展示输入框
        threshold, color = ShowThresholdInput(xmin, xmax)
        inputNum = float(threshold)
        # 生成配置
        config = model.ThresholdConfig(
            cfgId=cfgId,
            substance=substance.name,
            locaX=locatX,
            locaY=locatY,
            locaInd=locaInd,
            lineFillList = [model.LineFill(new_x, new_y, inputNum)],
            color=color
        )
         # todo:robin 看到这里了
        if cfgId in thd.ThresholdConfigMap :
            config = thd.ThresholdConfigMap[cfgId]
            newLineFillList = thd.AddFillLine(model.LineFill(new_x, new_y, inputNum), config.lineFillList)
            config.lineFillList = newLineFillList
        else :
            thd.ThresholdConfigMap[cfgId] = config
        # 保存配置
        thd.SaveThresholdConfig(thd.ThresholdConfigMap)
        # 关闭之前的窗口
        plt.close(new_fig)

        # 重新绘制
        drawInnerLine(substance, locatX, locatY, locaInd,curve,fig, axs)

    # 创建SpanSelector用于区间选择
    span_selector = SpanSelector(new_ax, onselect, 'horizontal', useblit=True, interactive=True,
                                 drag_from_anywhere=True)

    new_ax.set_xlabel('Wave Number')
    new_ax.set_ylabel('Intensity')
    new_ax.set_title(f'Intensity Curve for Point ({locatX}, {locatY})')

    # 连接关闭事件，当曲线图关闭时执行重绘散点图的函数
    # new_fig.canvas.mpl_connect('close_event', RedrawScatter(substance.name,fig, axs))

    plt.show()

# 重绘散点图
def RedrawScatter(substanceName, fig, axs):
    global current_curve_fig
    if current_curve_fig is not None:
        current_curve_fig.canvas.flush_events()
        current_curve_fig = None

    axs.clear()
    points, substance = data.ImportData(substanceName)
    DrawScatter(points, substance,fig, axs)

def CalScatterXRange(points):
    if len(points) == 0 :
        print("[CalScatterXRange]points is empty")
        return 0, 0
    locatXSet = {point.locaX for point in points}
    sortedXList = sorted(list(locatXSet))
    xDistance = sortedXList[1] - sortedXList[0]
    xMin = sortedXList[0] - xDistance / 2
    xMax = sortedXList[len(sortedXList) - 1] + xDistance / 2
    return xMin, xMax


def CalScatterYRange(points):
    if len(points) == 0 :
        print("[CalScatterXRange]points is empty")
        return 0, 0
    locatYSet = {point.locaY for point in points}
    sortedYList = sorted(list(locatYSet))
    yDistance = sortedYList[1] - sortedYList[0]
    yMin = sortedYList[0] - yDistance / 2
    yMax = sortedYList[len(sortedYList) - 1] + yDistance / 2
    return yMin, yMax

