import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QFormLayout
from PyQt5.QtGui import QPalette, QColor


app = QApplication(sys.argv)
widget = QWidget()

label = QLabel("Hello, World!")
palette = label.palette()
palette.setColor(QPalette.Background, QColor(255, 255, 0))  # 黄色
label.setPalette(palette)
label.setAutoFillBackground(True)
layout = QFormLayout()  # 假设你已经有合适的布局设置，如QVBoxLayout等，这里省略布局细节
layout.addWidget(label)
widget.setLayout(layout)
widget.show()
sys.exit(app.exec_())