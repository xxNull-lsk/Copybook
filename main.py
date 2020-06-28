import subprocess
import sys
from sys import platform

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QGridLayout
import datetime


page_width = 21
page_height = 29.7
start_x = 0.8
start_y = 1.5

doc_width = page_width - start_x * 2
doc_height = page_height - start_y * 2

col_count = 5
col_width = doc_width / col_count
# print('doc_width', doc_width, 'col_width', col_width)

line_space = 0.6
line_height = 1.5
line_color = 'lightgreen'
line_count = int((doc_height + line_space) / (line_height + line_space))
# print('line_count', line_count, (doc_height + line_space) / (line_height + line_space))
# col_text_colors = ['black', 'lightgrey']  # 第一行黑色，其余浅灰
col_text_colors = ['lightgrey']  # 全部浅灰

UseStdFont = False

if UseStdFont:
    font_name = 'Pinyinok'
    font_file = 'Pinyinok.ttf'
    font_size = 36
    font_scan = 0.75
else:
    font_name = 'Pinyinok2'
    font_file = 'Pinyinok2.ttf'
    font_size = 28
    font_scan = 0.67


def set_font(canv, size):
    pdfmetrics.registerFont(TTFont(font_name, font_file))
    canv.setFont(font_name, size)


def draw_4_line(canv, _x, _y):
    x = _x
    y = page_height - _y
    canv.setDash([])
    canv.line(x * cm, y * cm, (doc_width + x) * cm, y * cm)
    y -= line_height / 3
    canv.setDash([2, 2])
    canv.line(x * cm, y * cm, (doc_width + x) * cm, y * cm)
    y -= line_height / 3
    canv.line(x * cm, y * cm, (doc_width + x) * cm, y * cm)
    y -= line_height / 3
    canv.setDash([])
    canv.line(x * cm, y * cm, (doc_width + x) * cm, y * cm)

    for index in range(0, col_count + 1):
        x = _x + index * col_width
        canv.line(x * cm, y * cm, x * cm, (y + line_height) * cm)


def draw_bank(canv):
    canv.setStrokeColor(line_color)
    canv.setLineWidth(1)
    for row in range(0, line_count):
        x = start_x
        y = start_y + row * (line_height + line_space)
        draw_4_line(canv, x, y)


def draw_text(canv, row, col, txt, color=None):
    if txt == '' or txt is None:
        return
    if color is not None:
        canv.setFillColor(color)
    x = start_x + col * col_width
    y = start_y + row * (line_height + line_space) + line_height * font_scan
    txt_width = canv.stringWidth(txt)
    x += (col_width - txt_width / cm) / 2
    y = page_height - y  # 转换坐标系，右上角坐标系，转换成左下角
    canv.drawString(x * cm, y * cm, txt)


def draw_mutilate_text(canv, txt):
    curr_page = -1
    for index, t in enumerate(txt):
        page_index = int(index / col_count / line_count)
        if curr_page != page_index:
            if curr_page != -1:
                canv.showPage()
            # 设置字体及字号
            set_font(canv, font_size)
            draw_bank(canv)
            curr_page = page_index
        row = int(index / col_count) - line_count * curr_page
        col = int(index % col_count)
        if col >= len(col_text_colors):
            color = col_text_colors[-1]
        else:
            color = col_text_colors[col]
        draw_text(canv, row, col, t, color)


def draw_text_pre_line(canv, txt, repeat=False):
    curr_page = -1
    line_text = []
    for t in txt:
        line_text.append(t)
        for i in range(0, col_count - 1):
            line_text.append('' if not repeat else t)
    for index, t in enumerate(line_text):
        page_index = int(index / col_count / line_count)
        if curr_page != page_index:
            if curr_page != -1:
                canv.showPage()
            # 设置字体及字号
            set_font(canv, font_size)
            draw_bank(canv)
            curr_page = page_index
        row = int(index / col_count) - line_count * curr_page
        col = int(index % col_count)
        if col >= len(col_text_colors):
            color = col_text_colors[-1]
        else:
            color = col_text_colors[col]
        draw_text(canv, row, col, t, color)


def main():
    # 定义PDF文件存放文件名
    pdf_path = "test.pdf"
    # 建立文件
    canv = canvas.Canvas(pdf_path, pagesize=(page_width * cm, page_height * cm))

    txt = ['zheng', 'zhuang', 'xia', 'man', 'mai', 'ni', 'wo', 'ren', 'yu', 'rv', 'ni', 'hao', 'hai', 'di', 'ye',
           'xie', 'liu', 'wang', 'jiao', 'bao']

    draw_mutilate_text(canv, txt)
    canv.showPage()
    canv.save()
    if platform == 'win32':
        os.startfile(pdf_path)
    elif platform == 'linux':
        subprocess.call(["xdg-open", pdf_path])
    elif platform == 'darwin':
        subprocess.call(["open", pdf_path])


class MyApp:
    def on_click_ok(self):
        global col_text_colors, line_color
        txt = self.edit_text.toPlainText().split()
        pdf_path = self.edit_file_name.text()
        canv = canvas.Canvas(pdf_path, pagesize=(page_width * cm, page_height * cm))

        col_text_colors = self.combo_colors.currentData()
        line_color = self.combo_line_color.currentData()

        curr_type = self.combo_types.currentData()
        if curr_type == 0:
            draw_text_pre_line(canv, txt)
        elif curr_type == 1:
            draw_text_pre_line(canv, txt, repeat=True)
        elif curr_type == 2:
            draw_mutilate_text(canv, txt)
        canv.showPage()
        canv.save()
        if platform == 'win32':
            os.startfile(pdf_path)
        elif platform == 'linux':
            subprocess.call(["xdg-open", pdf_path])
        elif platform == 'darwin':
            subprocess.call(["open", pdf_path])

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        widget = QtWidgets.QWidget()
        widget.resize(360, 360)
        widget.setWindowTitle("hello, pyqt5")
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
        label = QtWidgets.QLabel("拼音")
        grid.addWidget(label, row, 0)
        self.edit_text = QtWidgets.QTextEdit('a b c d e f g h i j k l m n o p q r s t u v w x y z')
        grid.addWidget(self.edit_text, row, 1)

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
        grid.addWidget(self.combo_colors, row, 1)

        row += 1
        label = QtWidgets.QLabel("样式")
        grid.addWidget(label, row, 0)
        self.combo_types = QtWidgets.QComboBox()
        self.combo_types.addItem('每行仅打印首列', 0)
        self.combo_types.addItem('每行打印一个', 1)
        self.combo_types.addItem('常规', 2)
        grid.addWidget(self.combo_types, row, 1)

        row += 1
        btn_ok = QtWidgets.QPushButton("确认")
        btn_ok.clicked.connect(self.on_click_ok)
        grid.addWidget(btn_ok, row, 1, alignment=QtCore.Qt.AlignCenter)

        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = widget.geometry()
        widget.move((screen.width() - size.width()) / 2,
                    (screen.height() - size.height()) / 2)
        widget.show()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    app = MyApp()
