import datetime
import os
import subprocess
from sys import platform

import fitz
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption, QFontDatabase, QFont, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton, QHBoxLayout

from backend.PinYin import PinYin


class UiPinYin(QWidget):

    def __init__(self, font_path):
        super().__init__()
        self.font_path = font_path
        self.pinyin = PinYin(font_path=self.font_path)
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(32, 16, 32, 16)

        row = -1

        row += 1
        label = QLabel("文件名")
        grid.addWidget(label, row, 0)
        self.edit_file_name = QLineEdit(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.pdf')
        grid.addWidget(self.edit_file_name, row, 1)

        row += 1
        label = QLabel("线条颜色")
        grid.addWidget(label, row, 0)
        self.combo_line_color = QComboBox()
        self.combo_line_color.addItem('浅绿', 'rgb(199, 238, 206)')
        self.combo_line_color.addItem('粉色', 'lightpink')
        self.combo_line_color.addItem('黑色', 'black')
        grid.addWidget(self.combo_line_color, row, 1)
        self.combo_line_color.setCurrentIndex(1)

        row += 1
        label = QLabel("文字颜色")
        grid.addWidget(label, row, 0)
        self.combo_colors = QComboBox()
        self.combo_colors.addItem('首行黑色，其余浅灰', ['black', 'lightgrey'])
        self.combo_colors.addItem('全部黑色', ['black'])
        self.combo_colors.addItem('全部浅灰', ['lightgrey'])
        self.combo_colors.addItem('首行粉色，其余浅灰', ['lightpink', 'lightgrey'])
        self.combo_colors.addItem('全部粉色', ['lightpink'])
        grid.addWidget(self.combo_colors, row, 1)
        self.combo_colors.setCurrentIndex(4)

        row += 1
        label = QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QComboBox()
        self.combo_types.addItem('常规')
        self.combo_types.addItem('不描字')
        self.combo_types.addItem('半描字')
        self.combo_types.addItem('全描字')
        grid.addWidget(self.combo_types, row, 1)
        self.combo_types.setCurrentIndex(0)

        row += 1
        label = QLabel("声调")
        grid.addWidget(label, row, 0)
        self.edit_text2 = QTextEdit()
        self.edit_text2.setFixedHeight(148)
        self.edit_text2.setMinimumWidth(368)
        self.edit_text2.setReadOnly(True)
        self.edit_text2.setText('ā á ǎ à  '
                                'ō ó ǒ ò\n'
                                'ē é ě è  '
                                'ī  í  ǐ  ì\n'
                                'ū ú ǔ ù  '
                                'ǖ ǘ ǚ ǜ')
        self.edit_text2.setWordWrapMode(QTextOption.WrapAnywhere)
        grid.addWidget(self.edit_text2, row, 1)

        row += 1
        label = QLabel("拼音")
        grid.addWidget(label, row, 0)
        self.edit_text = QTextEdit()
        self.edit_text.setText('wǒ ài běi jīng tiān ān mén')
        self.edit_text.setWordWrapMode(QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        grid.addWidget(self.edit_text, row, 1)

        font_id = QFontDatabase.addApplicationFont(self.pinyin.font_file)
        fonts = QFontDatabase.applicationFontFamilies(font_id)
        if len(fonts) > 0:
            font = QFont()
            font.setFamily(fonts[0])
            font.setPointSize(24)
            self.edit_text.setFont(font)
            self.edit_text2.setFont(font)
        else:
            print("WARN: Load {} failed".format(self.pinyin.font_file))

        row += 1
        self.btn_ok = QPushButton("  生成拼音字帖  ")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.addLayout(grid)

        self.preview = QLabel()
        hbox.addWidget(self.preview)

        self.setLayout(hbox)

        self.combo_line_color.currentIndexChanged.connect(self.do_preview)
        self.combo_colors.currentIndexChanged.connect(self.do_preview)
        self.combo_types.currentIndexChanged.connect(self.do_preview)
        self.edit_text.textChanged.connect(self.do_preview)
        self.do_preview()

    def on_click_ok(self):
        self.btn_ok.setEnabled(False)
        try:
            pdf_path = self.edit_file_name.text()
            self.do_draw(pdf_path)
            # 打开
            if platform == 'win32':
                os.startfile(pdf_path)
            elif platform == 'linux':
                subprocess.call(["xdg-open", pdf_path])
            elif platform == 'darwin':
                subprocess.call(["open", pdf_path])
        finally:
            self.btn_ok.setEnabled(True)

    def do_draw(self, pdf_path):
        self.pinyin = PinYin(font_path=self.font_path)
        txt = self.edit_text.toPlainText().split()
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

    def do_preview(self):
        pdf_path = "/tmp/1.pdf"
        self.do_draw(pdf_path)
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
