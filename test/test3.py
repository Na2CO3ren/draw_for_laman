import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QStyledItemDelegate,QFormLayout
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt
import PyQt5.QtGui as QtGui

class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole)
        bgColor = QColor("lightblue")  # 设置背景色为浅蓝色，可根据需要修改
        painter.save()
        option.palette.setColor(QtGui.QPalette.Background, bgColor)
        QStyledItemDelegate.paint(self, painter, option, index)
        painter.restore()

app = QApplication(sys.argv)
widget = QWidget()
layout = QFormLayout()  # 省略布局细节
comboBox = QComboBox()
comboBox.addItems(["Option 1", "Option 2", "Option 3"])
delegate = CustomDelegate()
comboBox.setItemDelegate(delegate)
layout.addWidget(comboBox)
widget.setLayout(layout)
widget.show()
sys.exit(app.exec_())