import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QComboBox

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        # 第一个下拉选择框
        self.comboBox1 = QComboBox()
        self.comboBox1.addItems(["选项1", "选项2", "选项3"])
        layout.addRow("第一个选项", self.comboBox1)

        # 第二个下拉选择框
        self.comboBox2 = QComboBox()
        self.updateComboBox2Options()
        layout.addRow("第二个选项", self.comboBox2)

        # 连接信号和槽
        self.comboBox1.currentIndexChanged.connect(self.updateComboBox2Options)

        self.setLayout(layout)

    def updateComboBox2Options(self):
        selectedOption = self.comboBox1.currentText()
        if selectedOption == "选项1":
            self.comboBox2.clear()
            self.comboBox2.addItems(["子选项1 - 1", "子选项1 - 2"])
        elif selectedOption == "选项2":
            self.comboBox2.clear()
            self.comboBox2.addItems(["子选项2 - 1", "子选项2 - 2", "子选项2 - 3"])
        elif selectedOption == "选项3":
            self.comboBox2.clear()
            self.comboBox2.addItems(["子选项3 - 1"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())