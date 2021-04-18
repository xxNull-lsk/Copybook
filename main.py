import subprocess
import sys
from sys import platform
import os
import json

import fitz
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog
import datetime

from PinYin import PinYin
from HanZi import HanZi

if getattr(sys, 'frozen', False):  # 是否Bundle Resource
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
font_path = os.path.join(base_path, 'fonts')
font_cfg = {}


class UiHanZi(QtWidgets.QWidget):
    hanzi = None

    def load_fonts(self):
        global font_cfg
        # 加载字体配置
        with open(os.path.join(font_path, "手写.json"), 'r') as f:
            font_cfg = json.load(f)
        for f in font_cfg['fonts'].keys():
            font_cfg['fonts'][f]['font_file'] = os.path.join(font_path, "手写", font_cfg['fonts'][f]['font_file'])

        # 加载目录中的字体
        for f in os.listdir(os.path.join(font_path, "手写")):
            name = os.path.splitext(f)
            if name[-1] != '.ttf':
                continue
            if name[0] in font_cfg['fonts']:
                continue
            _cfg = font_cfg['base'].copy()
            _cfg['font_file'] = os.path.join(font_path, "手写", f)
            font_cfg['fonts'][name[0]] = _cfg

        # 校验文件在不在
        for f in font_cfg['fonts'].keys():
            if not os.path.exists(font_cfg['fonts'][f]['font_file']):
                del font_cfg['fonts'][f]

        self.hanzi = HanZi(font_cfg['fonts'])

    def __init__(self):
        global font_cfg
        super().__init__()

        self.load_fonts()

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(32, 16, 32, 16)

        row = -1

        row += 1
        label = QtWidgets.QLabel("线条颜色")
        grid.addWidget(label, row, 0)
        self.combo_line_color = QtWidgets.QComboBox()
        self.combo_line_color.addItem('红色', ['rgb(152, 15, 41)', 'lightpink'])
        self.combo_line_color.addItem('浅绿',  ['rgb(0, 176, 80)', 'rgb(199, 238, 206)'])
        self.combo_line_color.addItem('黑色', ['black', 'lightgrey'])
        self.combo_line_color.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_line_color, row, 1)

        row += 1
        label = QtWidgets.QLabel("方格类型")
        grid.addWidget(label, row, 0)
        self.combo_grid_type = QtWidgets.QComboBox()
        self.combo_grid_type.addItem('米字格', HanZi.GRID_TYPE_MI)
        self.combo_grid_type.addItem('田字格', HanZi.GRID_TYPE_TIAN)
        self.combo_grid_type.addItem('方格', HanZi.GRID_TYPE_FANG)
        self.combo_grid_type.addItem('回宫格', HanZi.GRID_TYPE_HUI)
        self.combo_grid_type.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_grid_type, row, 1)

        row += 1
        label = QtWidgets.QLabel("文字颜色")
        grid.addWidget(label, row, 0)
        self.combo_colors = QtWidgets.QComboBox()
        self.combo_colors.addItem('全部粉色', ['lightpink'])
        self.combo_colors.addItem('首行粉色，其余浅灰', ['lightpink', 'lightgrey'])
        self.combo_colors.addItem('全部浅绿', ['rgb(199, 238, 206)'])
        self.combo_colors.addItem('首行浅绿，其余浅灰', ['rgb(199, 238, 206)', 'lightgrey'])
        self.combo_colors.addItem('全部黑色', ['black'])
        self.combo_colors.addItem('全部浅灰', ['lightgrey'])
        self.combo_colors.addItem('首行黑色，其余浅灰', ['black', 'lightgrey'])
        self.combo_colors.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_colors, row, 1)

        row += 1
        label = QtWidgets.QLabel("字体")
        grid.addWidget(label, row, 0)
        self.combo_fonts = QtWidgets.QComboBox()
        fonts = list(self.hanzi.fonts.keys())
        # fonts.sort()
        for font_name in fonts:
            self.combo_fonts.addItem(font_name)
        self.combo_fonts.setCurrentText(font_cfg['default'])
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
        self.combo_types.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        label = QtWidgets.QLabel("内容")
        grid.addWidget(label, row, 0)
        self.edit_text = QtWidgets.QTextEdit()
        self.edit_text.setText(font_cfg['text'])
        self.edit_text.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        self.edit_text.textChanged.connect(self.do_preview)
        grid.addWidget(self.edit_text, row, 1)

        row += 1
        self.btn_ok = QtWidgets.QPushButton("生成汉字字帖")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=QtCore.Qt.AlignCenter)

        vbox = QHBoxLayout()
        vbox.addLayout(grid)

        self.preview = QLabel()
        vbox.addWidget(self.preview)

        self.setLayout(vbox)

        self.on_font_changed()

    def do_draw(self, pdf_path, max_page_count):
        hanzi = HanZi(font_cfg['fonts'], max_page_count)
        try:
            txt = self.edit_text.toPlainText()
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
        finally:
            hanzi.close()
        return pdf_path

    def do_preview(self):
        pdf_path = "/tmp/1.pdf"
        self.do_draw(pdf_path, 1)
        with fitz.open(pdf_path) as doc:
            if doc.page_count <= 0:
                return
            page = doc[0]
            img = page.get_pixmap()

        os.remove(pdf_path)
        fmt = QImage.Format_RGBA8888 if img.alpha else QImage.Format_RGB888
        img = QImage(img.samples, img.width, img.height, img.stride, fmt)
        self.preview.setPixmap(QPixmap(img))
        self.preview.setFixedWidth(img.width())

    def on_click_ok(self):
        try:
            pdf_path, _ = QFileDialog.getSaveFileName(parent=self, caption="open file", filter='PDF files(*.pdf)')
            if pdf_path is None or pdf_path == '':
                return
            self.do_draw(pdf_path, -1)

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
        self.do_preview()


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
        self.combo_line_color.setCurrentIndex(1)

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
        self.combo_colors.setCurrentIndex(4)

        row += 1
        label = QtWidgets.QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QtWidgets.QComboBox()
        self.combo_types.addItem('常规')
        self.combo_types.addItem('不描字')
        self.combo_types.addItem('半描字')
        self.combo_types.addItem('全描字')
        grid.addWidget(self.combo_types, row, 1)
        self.combo_types.setCurrentIndex(0)

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
