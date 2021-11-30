import json

import fitz
import os
import platform
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QTextOption, QFontDatabase, QFont
from PyQt5.QtWidgets import QFileDialog, QGridLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit, QComboBox, QWidget

from backend.Number import Number


class UiNumber(QWidget):
    number = None
    font_cfg = {}

    def load_fonts(self):
        # 加载字体配置
        with open(os.path.join(self.font_path, "数字.json"), 'r') as f:
            self.font_cfg = json.load(f)
        for f in self.font_cfg['fonts'].keys():
            self.font_cfg['fonts'][f]['font_file'] = os.path.join(
                self.font_path,
                "手写",
                self.font_cfg['fonts'][f]['font_file'])

        # 加载目录中的字体
        for f in os.listdir(os.path.join(self.font_path, "手写")):
            name = os.path.splitext(f)
            if name[-1] != '.ttf' or name[0] in self.font_cfg["skip"]:
                continue
            if name[0] in self.font_cfg['fonts']:
                continue
            _cfg = self.font_cfg['base'].copy()
            _cfg['font_file'] = os.path.join(self.font_path, "手写", f)
            self.font_cfg['fonts'][name[0]] = _cfg

        # 校验文件在不在
        for f in self.font_cfg['fonts'].keys():
            if not os.path.exists(self.font_cfg['fonts'][f]['font_file']):
                del self.font_cfg['fonts'][f]

        self.number = Number(self.font_cfg['fonts'])

    def __init__(self, font_path):
        super().__init__()
        self.font_path = font_path
        self.load_fonts()

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(32, 16, 32, 16)

        row = -1

        row += 1
        label = QLabel("线条颜色")
        grid.addWidget(label, row, 0)
        self.combo_line_color = QComboBox()
        self.combo_line_color.addItem('红色', ['rgb(152, 15, 41)', 'lightpink'])
        self.combo_line_color.addItem('浅绿',  ['rgb(0, 176, 80)', 'rgb(199, 238, 206)'])
        self.combo_line_color.addItem('黑色', ['black', 'lightgrey'])
        self.combo_line_color.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_line_color, row, 1)

        row += 1
        label = QLabel("文字颜色")
        grid.addWidget(label, row, 0)
        self.combo_colors = QComboBox()
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
        label = QLabel("字体")
        grid.addWidget(label, row, 0)
        self.combo_fonts = QComboBox()
        fonts = list(self.number.fonts.keys())
        # fonts.sort()
        for font_name in fonts:
            self.combo_fonts.addItem(font_name)
        self.combo_fonts.setCurrentText(self.font_cfg['default'])
        self.combo_fonts.currentIndexChanged.connect(self.on_font_changed)
        grid.addWidget(self.combo_fonts, row, 1)

        row += 1
        label = QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QComboBox()
        self.combo_types.addItem('常规')
        self.combo_types.addItem('不描字')
        self.combo_types.addItem('半描字')
        self.combo_types.addItem('全描字')
        self.combo_types.setCurrentIndex(1)
        self.combo_types.currentIndexChanged.connect(self.do_preview)
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        label = QLabel("内容")
        grid.addWidget(label, row, 0)
        self.edit_text = QTextEdit()
        self.edit_text.setText(self.font_cfg['text'])
        self.edit_text.setWordWrapMode(QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        self.edit_text.textChanged.connect(self.do_preview)
        grid.addWidget(self.edit_text, row, 1)

        row += 1
        self.btn_ok = QPushButton("  生成数字字帖  ")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.addLayout(grid)

        self.preview = QLabel()
        hbox.addWidget(self.preview)

        self.setLayout(hbox)

        self.on_font_changed()

    def do_draw(self, pdf_path, max_page_count):
        num = Number(self.font_cfg['fonts'], max_page_count)
        try:
            txt = self.edit_text.toPlainText()
            num.create(pdf_path)

            num.col_text_colors = self.combo_colors.currentData()
            num.line_color = self.combo_line_color.currentData()
            num.set_font(self.combo_fonts.currentText())

            if txt == '':
                num.draw_bank()
            else:
                curr_type = self.combo_types.currentText()
                if curr_type == '不描字':
                    num.draw_text_pre_line(txt)
                elif curr_type == '全描字':
                    num.draw_text_pre_line(txt, repeat=1)
                elif curr_type == '半描字':
                    num.draw_text_pre_line(txt, repeat=0.5)
                elif curr_type == '常规':
                    num.draw_mutilate_text(txt)
        finally:
            num.close()
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
        font_id = QFontDatabase.addApplicationFont(self.number.fonts[font_name]['font_file'])
        fonts = QFontDatabase.applicationFontFamilies(font_id)
        if len(fonts) > 0:
            font = QFont()
            font.setFamily(fonts[0])
            font.setPointSize(18)
            self.edit_text.setFont(font)
        else:
            print("WARN: Load {} failed".format(self.hanzi.fonts[font_name]['font_file']))
        self.do_preview()
