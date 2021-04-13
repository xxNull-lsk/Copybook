import subprocess
import sys
from sys import platform
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGridLayout
import datetime

from PinYin import PinYin
from HanZi import HanZi

if getattr(sys, 'frozen', False):  # 是否Bundle Resource
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
font_path = os.path.join(base_path, 'fonts')


class UiHanZi(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
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
        self.combo_line_color.addItem('浅绿',  'rgb(199, 238, 206)')
        self.combo_line_color.addItem('粉色', 'lightpink')
        self.combo_line_color.addItem('黑色', 'black')
        grid.addWidget(self.combo_line_color, row, 1)

        row += 1
        label = QtWidgets.QLabel("方格类型")
        grid.addWidget(label, row, 0)
        self.combo_grid_type = QtWidgets.QComboBox()
        self.combo_grid_type.addItem('米字格', HanZi.GRID_TYPE_MI)
        self.combo_grid_type.addItem('田字格', HanZi.GRID_TYPE_TIAN)
        self.combo_grid_type.addItem('方格', HanZi.GRID_TYPE_FANG)
        self.combo_grid_type.addItem('回宫格', HanZi.GRID_TYPE_HUI)
        grid.addWidget(self.combo_grid_type, row, 1)

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
        label = QtWidgets.QLabel("字体")
        grid.addWidget(label, row, 0)
        self.combo_fonts = QtWidgets.QComboBox()
        self.hanzi = HanZi(font_path)
        fonts = list(self.hanzi.fonts.keys())
        # fonts.sort()
        for font_name in fonts:
            self.combo_fonts.addItem(font_name)
        self.combo_fonts.currentIndexChanged.connect(self.on_font_changed)
        grid.addWidget(self.combo_fonts, row, 1)

        row += 1
        label = QtWidgets.QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QtWidgets.QComboBox()
        self.combo_types.addItem('常规')
        self.combo_types.addItem('不描字')
        self.combo_types.addItem('半描字')
        self.combo_types.addItem('全描字')
        self.combo_types.setCurrentText('全描字')
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        label = QtWidgets.QLabel("内容")
        grid.addWidget(label, row, 0)
        self.edit_text = QtWidgets.QTextEdit()
        self.edit_text.setText('内容')
        self.edit_text.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        grid.addWidget(self.edit_text, row, 1)

        row += 1
        self.btn_ok = QtWidgets.QPushButton("生成汉字字帖")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=QtCore.Qt.AlignCenter)
        self.on_font_changed()

    def on_click_ok(self):
        hanzi = HanZi(font_path)
        try:
            txt = self.edit_text.toPlainText()
            pdf_path = self.edit_file_name.text()
            hanzi.create(pdf_path)

            hanzi.col_text_colors = self.combo_colors.currentData()
            hanzi.line_color = self.combo_line_color.currentData()
            hanzi.grid_type = self.combo_grid_type.currentData()
            hanzi.set_font(self.combo_fonts.currentText())

            if txt == '':
                hanzi.draw_bank()
            else:
                curr_type = self.combo_types.currentText()
                if curr_type == '不描字':
                    hanzi.draw_text_pre_line(txt)
                elif curr_type == '全描字':
                    hanzi.draw_text_pre_line(txt, repeat=1)
                elif curr_type == '半描字':
                    hanzi.draw_text_pre_line(txt, repeat=0.5)
                elif curr_type == '常规':
                    hanzi.draw_mutilate_text(txt)

            hanzi.close()

            # 预览
            if platform == 'win32':
                os.startfile(pdf_path)
            elif platform == 'linux':
                subprocess.call(["xdg-open", pdf_path])
            elif platform == 'darwin':
                subprocess.call(["open", pdf_path])
        finally:
            self.btn_ok.setEnabled(True)

    def on_font_changed(self):
        font_name = self.combo_fonts.currentText()
        font_id = QtGui.QFontDatabase.addApplicationFont(self.hanzi.fonts[font_name]['font_file'])
        fonts = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if len(fonts) > 0:
            font = QtGui.QFont()
            font.setFamily(fonts[0])
            font.setPointSize(18)
            self.edit_text.setFont(font)
        else:
            print("WARN: Load {} failed".format(self.hanzi.fonts[font_name]['font_file']))


class UiPinYin(QtWidgets.QWidget):
    pinyin = PinYin(font_path=font_path)

    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
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
        self.combo_line_color.addItem('浅绿', 'rgb(199, 238, 206)')
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
        self.combo_types.setCurrentText('全描字')
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
        if len(fonts) > 0:
            font = QtGui.QFont()
            font.setFamily(fonts[0])
            font.setPointSize(24)
            self.edit_text.setFont(font)
            self.edit_text2.setFont(font)
        else:
            print("WARN: Load {} failed".format(self.pinyin.font_file))

        row += 1
        self.btn_ok = QtWidgets.QPushButton("生成拼音字帖")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=QtCore.Qt.AlignCenter)

    def on_click_ok(self):
        self.pinyin = PinYin(font_path=font_path)
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


class MyMainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=QtWidgets.QDesktopWidget())
        self.resize(360, 360)
        self.setWindowTitle("字帖生成器")
        self.setWindowIcon(QtGui.QIcon(os.path.join(base_path, 'app.ico')))

        self.root_layout = QtWidgets.QHBoxLayout(self)

        # 初始化右侧布局
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(20)
        self.right_layout.setAlignment(QtCore.Qt.AlignTop)
        self.btn_pinyin = QtWidgets.QPushButton('拼音')
        # self.btn_pinyin.setIcon()
        self.btn_pinyin.setFixedWidth(120)
        self.btn_pinyin.clicked.connect(self.on_pinyin)
        self.right_layout.addWidget(self.btn_pinyin)
        self.btn_hanzi = QtWidgets.QPushButton('汉字')
        # self.btn_haizi.setIcon()
        self.btn_hanzi.setFixedWidth(120)
        self.btn_hanzi.clicked.connect(self.on_hanzi)
        self.right_layout.addWidget(self.btn_hanzi)

        # 初始化左侧布局
        self.left_layout = QtWidgets.QStackedLayout()
        self.pinyin = UiPinYin()
        self.left_layout.addWidget(self.pinyin)
        self.hanzi = UiHanZi()
        self.left_layout.addWidget(self.hanzi)

        # 初始化整体布局
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.addLayout(self.right_layout)
        self.root_layout.addLayout(self.left_layout)

        # 显示窗口
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def on_pinyin(self):
        self.btn_pinyin.setFocus()
        self.left_layout.setCurrentIndex(0)

    def on_hanzi(self):
        self.btn_hanzi.setFocus()
        self.left_layout.setCurrentIndex(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MyMainWindow()
    ex.show()
    sys.exit(app.exec())
