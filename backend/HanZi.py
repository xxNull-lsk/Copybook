from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab import rl_config
import os


class HanZi:
    canv = None
    curr_page = -1
    curr_index = -1

    GRID_TYPE_MI = 0
    GRID_TYPE_TIAN = 1
    GRID_TYPE_FANG = 2
    GRID_TYPE_HUI = 3

    def set_font(self, font_name):
        if font_name not in self.fonts.keys():
            return False
        self.font_name = font_name + '1'
        self.font_file = self.fonts[font_name]['font_file']
        self.font_size = self.fonts[font_name]['font_size']
        self.font_scan = self.fonts[font_name]['font_scan']
        return True

    def __init__(self, font_path, page_width=21, page_height=29.7, col_count=12, row_count=15, font_name='楷体'):
        self.fonts = {
            '楷体': {
                'font_file': os.path.join(font_path, '楷体_GB2312.ttf'),
                'font_size': 38,
                'font_scan': 0.85
            },
            '华文楷体': {
                'font_file': os.path.join(font_path, '华文楷体.ttf'),
                'font_size': 38,
                'font_scan': 0.82
            },
            '庞中华钢笔字体': {
                'font_file': os.path.join(font_path, '庞中华钢笔字体.ttf'),
                'font_size': 38,
                'font_scan': 0.8
            },
            '田英章楷书': {
                'font_file': os.path.join(font_path, '田英章楷书.ttf'),
                'font_size': 38,
                'font_scan': 0.8
            },
            '战加东硬笔楷书': {
                'font_file': os.path.join(font_path, '战加东硬笔楷书.ttf'),
                'font_size': 38,
                'font_scan': 0.85
            },
            '蝉羽真颜金戈': {
                'font_file': os.path.join(font_path, '蝉羽真颜金戈.ttf'),
                'font_size': 38,
                'font_scan': 0.82
            },
            '博洋楷体7000': {
                'font_file': os.path.join(font_path, '博洋楷体7000.ttf'),
                'font_size': 38,
                'font_scan': 0.85
            }
        }
        self.font_name = font_name + '1'
        self.font_file = self.fonts[font_name]['font_file']
        self.font_size = self.fonts[font_name]['font_size']
        self.font_scan = self.fonts[font_name]['font_scan']
        self.grid_type = self.GRID_TYPE_MI

        self.page_width = page_width
        self.page_height = page_height

        self.item_width = 1.5
        self.item_height = 1.5

        self.line_space = 0.2

        self.doc_width = col_count * self.item_width
        self.doc_height = row_count * self.item_height + (row_count - 1) * self.line_space
        if self.doc_height > self.page_height:
            max_doc_height = self.page_height - self.line_space * 2
            row_count = int((max_doc_height + self.line_space) / (self.item_height + self.line_space))
            self.doc_height = row_count * self.item_height + (row_count - 1) * self.line_space

        self.start_x = (self.page_width - self.doc_width) / 2
        self.start_y = (self.page_height - self.doc_height) / 2

        self.line_color = colors.Color(199, 238, 206)
        self.col_text_colors = ['lightgrey']  # 全部浅灰

        self.col_count = col_count
        print('doc_width', self.doc_width, 'col_count', self.col_count, col_count)
        self.row_count = row_count
        print('doc_height', self.doc_height, 'row_count', self.row_count, row_count)

    def __del__(self):
        self.close()

    def close(self):
        if self.canv is not None:
            self.canv.showPage()
            self.canv.save()
            self.canv = None

    def create(self, pdf_path):
        self.canv = canvas.Canvas(pdf_path, pagesize=(self.page_width * cm, self.page_height * cm))

    def _set_font(self, size):
        print(self.font_name, self.font_file)
        rl_config.autoGenerateMissingTTFName = True
        pdfmetrics.registerFont(TTFont(self.font_name, self.font_file))
        self.canv.setFont(self.font_name, size)

    def _draw_fang(self, _x, _y):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        # self.canv.setDash([2, 2])
        # self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        for index in range(0, self.col_count * 2 + 1):
            if index % 2 == 1:
                # self.canv.setDash([2, 2])
                continue
            else:
                self.canv.setDash([])
            x = _x + index * self.item_width / 2
            self.canv.line(x * cm, y * cm, x * cm, (y + self.item_height) * cm)

    def _draw_hui(self, _x, _y):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        for col in range(0, self.col_count + 1):
            x = _x + col * self.item_width
            self.canv.line(x * cm, y * cm, x * cm, (y + self.item_height) * cm)

        height = self.item_height * 0.7  # 该比例不一定正确。没有找到相关资料。该比例是量出来的。
        width = height * 0.618
        y = self.page_height - _y - (self.item_height - height) / 2
        for col in range(0, self.col_count):
            x = _x + col * self.item_width + (self.item_width - width) / 2
            self.canv.rect(x * cm, y * cm, width * cm, -height * cm)

    def _draw_tian(self, _x, _y):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        self.canv.setDash([2, 2])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        for index in range(0, self.col_count * 2 + 1):
            if index % 2 == 1:
                self.canv.setDash([2, 2])
            else:
                self.canv.setDash([])
            x = _x + index * self.item_width / 2
            self.canv.line(x * cm, y * cm, x * cm, (y + self.item_height) * cm)

    def _draw_mi(self, _x, _y):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        self.canv.setDash([2, 2])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.item_height / 2
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        for index in range(0, self.col_count * 2 + 1):
            if index % 2 == 1:
                self.canv.setDash([2, 2])
            else:
                self.canv.setDash([])
            x = _x + index * self.item_width / 2
            self.canv.line(x * cm, y * cm, x * cm, (y + self.item_height) * cm)

        for index in range(0, self.col_count):
            self.canv.setDash([2, 2])
            x = _x + index * self.item_width
            self.canv.line(x * cm, y * cm, (x + self.item_width) * cm, (y + self.item_height) * cm)
            self.canv.line((x + self.item_width) * cm, y * cm, x * cm, (y + self.item_height) * cm)

    def draw_bank(self):
        self.canv.setStrokeColor(self.line_color)
        self.canv.setLineWidth(1)
        for row in range(0, self.row_count):
            x = self.start_x
            y = self.start_y + row * (self.item_height + self.line_space)
            if self.grid_type == self.GRID_TYPE_MI:
                self._draw_mi(x, y)
            elif self.grid_type == self.GRID_TYPE_TIAN:
                self._draw_tian(x, y)
            elif self.grid_type == self.GRID_TYPE_FANG:
                self._draw_fang(x, y)
            elif self.grid_type == self.GRID_TYPE_HUI:
                self._draw_hui(x, y)

    def _next(self):
        self.curr_index = self.curr_index + 1
        page_index = int(self.curr_index / self.col_count / self.row_count)
        if self.curr_page != page_index:
            if self.curr_page != -1:
                self.canv.showPage()
            # 设置字体及字号
            self._set_font(self.font_size)
            self.draw_bank()
            self.curr_page = page_index

        row = int(self.curr_index / self.col_count) - self.row_count * self.curr_page
        col = int(self.curr_index % self.col_count)
        return row, col

    def draw_text(self, txt, color=None):
        row, col = self._next()
        if txt == '' or txt is None:
            return

        if color is None:
            if col >= len(self.col_text_colors):
                color = self.col_text_colors[-1]
            else:
                color = self.col_text_colors[col]

        if color is not None:
            self.canv.setFillColor(color)

        x = self.start_x + col * self.item_width
        y = self.start_y + row * (self.item_height + self.line_space) + self.item_height * self.font_scan
        txt_width = self.canv.stringWidth(txt)
        x += (self.item_width - txt_width / cm) / 2
        y = self.page_height - y  # 转换坐标系，右上角坐标系，转换成左下角
        self.canv.drawString(x * cm, y * cm, txt)

    def draw_mutilate_text(self, txt):
        txt = txt.strip()
        txt = txt.replace('\t', '')
        txt = txt.replace('\r', '')
        txt = txt.replace('\n\n', '\n')
        for t in txt:
            if t == '\n':
                while True:
                    col = int(self.curr_index % self.col_count)
                    if col == self.col_count - 1:
                        break
                    self._next()
                continue
            self.draw_text(t)

    def draw_text_pre_line(self, txt, repeat=0.0):
        txt = txt.strip()
        txt = txt.replace('\t', '')
        txt = txt.replace('\r', '')
        txt = txt.replace('\n', '')
        txt = txt.replace('，', '')
        txt = txt.replace('。', '')
        txt = txt.replace('？', '')
        txt = txt.replace('！', '')
        line_text = []
        # 填充，每行数据
        for t in txt:
            line_text.append(t)
            for i in range(0, self.col_count - 1):
                if (i + 1) / self.col_count > repeat:
                    line_text.append('')
                else:
                    line_text.append(t)
        for t in line_text:
            self.draw_text(t)
