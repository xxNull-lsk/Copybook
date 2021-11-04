import datetime
import os
import subprocess
from sys import platform

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont, QTextOption
from PyQt5.QtWidgets import QPushButton, QTextEdit, QLabel, QComboBox, QLineEdit, QGridLayout, QWidget

from backend.HanZi import HanZi


class UiHanZi(QWidget):

    def __init__(self, font_path):
        super().__init__()
        self.font_path = font_path
        grid = QGridLayout()
        self.setLayout(grid)
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
        self.combo_line_color.addItem('浅绿',  'rgb(199, 238, 206)')
        self.combo_line_color.addItem('粉色', 'lightpink')
        self.combo_line_color.addItem('黑色', 'black')
        grid.addWidget(self.combo_line_color, row, 1)

        row += 1
        label = QLabel("方格类型")
        grid.addWidget(label, row, 0)
        self.combo_grid_type = QComboBox()
        self.combo_grid_type.addItem('米字格', HanZi.GRID_TYPE_MI)
        self.combo_grid_type.addItem('田字格', HanZi.GRID_TYPE_TIAN)
        self.combo_grid_type.addItem('方格', HanZi.GRID_TYPE_FANG)
        self.combo_grid_type.addItem('回宫格', HanZi.GRID_TYPE_HUI)
        grid.addWidget(self.combo_grid_type, row, 1)

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

        row += 1
        label = QLabel("字体")
        grid.addWidget(label, row, 0)
        self.combo_fonts = QComboBox()
        self.hanzi = HanZi(self.font_path)
        fonts = list(self.hanzi.fonts.keys())
        # fonts.sort()
        for font_name in fonts:
            self.combo_fonts.addItem(font_name)
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
        self.combo_types.setCurrentText('全描字')
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        label = QLabel("内容")
        grid.addWidget(label, row, 0)
        self.edit_text = QTextEdit()
        self.edit_text.setAcceptRichText(False)
        self.edit_text.setText('内容')
        self.edit_text.setWordWrapMode(QTextOption.WrapAnywhere)
        self.edit_text.setMinimumWidth(260)
        self.edit_text.setMinimumHeight(150)
        grid.addWidget(self.edit_text, row, 1)

        row += 1
        self.btn_ok = QPushButton("  生成汉字字帖  ")
        self.btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(self.btn_ok, row, 1, alignment=Qt.AlignCenter)
        self.on_font_changed()

    def on_click_ok(self):
        hanzi = HanZi(self.font_path)
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
        font_id = QFontDatabase.addApplicationFont(self.hanzi.fonts[font_name]['font_file'])
        fonts = QFontDatabase.applicationFontFamilies(font_id)
        if len(fonts) > 0:
            font = QFont()
            font.setFamily(fonts[0])
            font.setPointSize(18)
            self.edit_text.setFont(font)
        else:
            print("WARN: Load {} failed".format(self.hanzi.fonts[font_name]['font_file']))