from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QFormLayout,QComboBox
from PyQt5.QtCore import Qt, QObject,QEvent
from PyQt5.QtGui import QPalette, QColor
import sys
import page_show as show
import model.model as model
import threshold as thd
import util.util as util
import const.color as cl

class DebugEventFilter(QObject):
    def eventFilter(self, watched, event):
        # print(f"事件过滤器正在处理事件，事件类型: {event.type()}，目标部件: {watched}")
        if event.type() == QEvent.Close and isinstance(watched, QWidget):
            watched.hide()  # 将窗口隐藏
            event.ignore()  # 忽略关闭事件
            print("通过事件过滤器拦截，窗口已隐藏，而不是关闭")
            return True
        return False

class MyWidget(QWidget):
    def __init__(self, x, y, new_x, new_y,config, substance, locaInd, scatter_plot, new_ax):
        app = QApplication(sys.argv)
        super().__init__()

        self.window = QWidget()
        self.window.setWindowTitle("阈值输入")

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft)

        # 前两行展示包含变量x的文本
        self.xMinLabel = QLabel(f'{x}')
        self.xMaxLabel = QLabel(f'{y}')
        layout.addRow("xMin:", self.xMinLabel)
        layout.addRow("xMax:", self.xMaxLabel)
        # 第三行创建可输入的文本框
        self.threshold_edit = QLineEdit()
        layout.addRow("threshold input:", self.threshold_edit)

        mainColor = show.GetMainColor(config.color)
        # 第四行和第五行创建颜色下拉列表
        self.comboBox1 = QComboBox()
        self.comboBox1.addItems(cl.MainPointColor)
        self.comboBox1.setCurrentText(mainColor)
        layout.addRow("color type:", self.comboBox1)

        self.comboBox2 = QComboBox()
        self.comboBox2.addItems(cl.SubColorMap[cl.MainPointColor[0]])
        layout.addRow("sub color type:", self.comboBox2)
        self.comboBox2.setCurrentText(config.color)

        # 颜色展示框
        displayLabel = QLabel('         ')
        layout.addRow("display color:", displayLabel)

        # 主颜色和子颜色的联动
        def comboBox1ChangeEvent():
            selectedOption = self.comboBox1.currentText()
            self.comboBox2.clear()
            self.comboBox2.addItems(cl.SubColorMap[selectedOption])

        self.comboBox1.currentIndexChanged.connect(comboBox1ChangeEvent)

        # 子颜色变化的时候 动态调整颜色展示框
        def comboBox2ChangeEvent():
            selectedOption = self.comboBox2.currentText()
            color = QColor(selectedOption)
            palette = displayLabel.palette()
            palette.setColor(QPalette.Background, color)
            displayLabel.setPalette(palette)
            displayLabel.setAutoFillBackground(True)

        comboBox2ChangeEvent()  # 先调用一次
        self.comboBox2.currentIndexChanged.connect(comboBox2ChangeEvent)
        submit_button = QPushButton("提交")
        submit_button.clicked.connect(self.refresh)
        layout.addWidget(submit_button)
        self.config = config
        self.new_x = new_x
        self.new_y = new_y
        self.substance = substance
        self.locaInd = locaInd
        self.scatter_plot = scatter_plot
        self.new_ax = new_ax
        self.window.setLayout(layout)
        self.app = app

    def execute(self):
        event_filter = DebugEventFilter()
        self.window.installEventFilter(event_filter)
        self.window.show()
        rt = self.app.exec_()
        print('execution end!!!')

    def refresh(self):
        threshold = self.threshold_edit.text()
        inputNum = float(threshold)
        newLineFillList = thd.AddFillLine(model.LineFill(self.new_x, self.new_y, inputNum), self.config.lineFillList)
        self.config.lineFillList = newLineFillList
        inputColor = self.comboBox2.currentText()
        self.config.color = inputColor
        # self.close()
        show.RefreshAfterInput(self.substance, self.locaInd, self.config, self.scatter_plot, self.new_ax)

    def showWin(self, x, y, new_x, new_y,config, substance, locaInd, scatter_plot, new_ax):
        self.xMinLabel.setText(f'{x}')
        self.xMaxLabel.setText(f'{y}')
        self.config = config
        self.new_x = new_x
        self.new_y = new_y
        self.substance = substance
        self.locaInd = locaInd
        self.scatter_plot = scatter_plot
        self.new_ax = new_ax
        # self.window.setVisible(True)
        # self.window.setHidden(False)
        self.window.show()