import subprocess
import sys
from sys import platform
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGridLayout
import datetime

from PinYin import PinYin


class MyApp:
    pinyin = PinYin()

    def on_click_ok(self):
        self.pinyin = PinYin()
        self.btn_ok.setEnabled(False)
        try:
            txt = self.edit_text.toPlainText().split()
            pdf_path = self.edit_file_name.text()
            self.pinyin.create(pdf_path)

            self.pinyin.col_text_colors = self.combo_colors.currentData()
            self.pinyin.line_color = self.combo_line_color.currentData()

            curr_type = self.combo_types.currentText()
            if curr_type == '不描字':
                self.pinyin.draw_text_pre_line(txt)
            elif curr_type == '全描字':
                self.pinyin.draw_text_pre_line(txt, repeat=1)
            elif curr_type == '半描字':
                self.pinyin.draw_text_pre_line(txt, repeat=0.5)
            elif curr_type == '常规':
                self.pinyin.draw_mutilate_text(txt)

            self.pinyin.close()

            # 预览
            if platform == 'win32':
                os.startfile(pdf_path)
            elif platform == 'linux':
                subprocess.call(["xdg-open", pdf_path])
            elif platform == 'darwin':
                subprocess.call(["open", pdf_path])
        finally:
            self.btn_ok.setEnabled(True)

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        widget = QtWidgets.QWidget()
        widget.resize(360, 360)
        widget.setWindowTitle("字帖生成器")
        
        grid = QGridLayout()
        widget.setLayout(grid)
        grid.setSpacing(16)
        grid.setContentsMargins(32, 16, 32, 16)

        row = -1

        row += 1
        label = QtWidgets.QLabel("文件名")
        grid.addWidget(label, row, 0)
        self.edit_file_name = QtWidgets.QLineEdit(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.pdf')
        grid.addWidget(self.edit_file_name, row, 1)

        row += 1
        label = QtWidgets.QLabel("线条颜色")
        grid.addWidget(label, row, 0)
        self.combo_line_color = QtWidgets.QComboBox()
        self.combo_line_color.addItem('浅绿', 'lightgreen')
        self.combo_line_color.addItem('粉色', 'lightpink')
        self.combo_line_color.addItem('黑色', 'black')
        grid.addWidget(self.combo_line_color, row, 1)

        row += 1
        label = QtWidgets.QLabel("文字颜色")
        grid.addWidget(label, row, 0)
        self.combo_colors = QtWidgets.QComboBox()
        self.combo_colors.addItem('首行黑色，其余浅灰', ['black', 'lightgrey'])
        self.combo_colors.addItem('全部黑色', ['black'])
        self.combo_colors.addItem('全部浅灰', ['lightgrey'])
        self.combo_colors.addItem('首行粉色，其余浅灰', ['lightpink', 'lightgrey'])
        self.combo_colors.addItem('全部粉色', ['lightpink'])
        grid.addWidget(self.combo_colors, row, 1)

        row += 1
        label = QtWidgets.QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QtWidgets.QComboBox()
        self.combo_types.addItem('常规')
        self.combo_types.addItem('不描字')
        self.combo_types.addItem('半描字')
        self.combo_types.addItem('全描字')
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        label = QtWidgets.QLabel("声调")
        grid.addWidget(label, row, 0)
        self.edit_text2 = QtWidgets.QTextEdit()
        self.edit_text2.setFixedHeight(86)
        self.edit_text2.setMinimumWidth(368)
        self.edit_text2.setReadOnly(True)
        self.edit_text2.setText('ā á ǎ à  '
                                'ō ó ǒ ò  '
                                'ē é ě è\n'
                                ' ī  í  ǐ  ì   '
                                'ū ú ǔ ù  '
                                'ǖ ǘ ǚ ǜ')
        self.edit_text2.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        grid.addWidget(self.edit_text2, row, 1)

        row += 1
        label = QtWidgets.QLabel("拼音")
        grid.addWidget(label, row, 0)
        self.edit_text = QtWidgets.QTextEdit()
        self.edit_text.setText('a b c d e f g h i j k l m n o p q r s t u v w x y z')
        self.edit_text.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        grid.addWidget(self.edit_text, row, 1)

        font_id = QtGui.QFontDatabase.addApplicationFont(self.pinyin.font_file)
        fonts = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        font = QtGui.QFont()
        font.setFamily(fonts[0])
        font.setPointSize(24)
        self.edit_text.setFont(font)
        self.edit_text2.setFont(font)

        row += 1
        self.btn_ok = QtWidgets.QPushButton("确认")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=QtCore.Qt.AlignCenter)

        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = widget.geometry()
        widget.move(int((screen.width() - size.width()) / 2),
                    int((screen.height() - size.height()) / 2))
        widget.show()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    app = MyApp()
