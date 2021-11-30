from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab import rl_config


class Number:
    canv = None
    curr_page = -1
    curr_index = -1

    def set_font(self, font_name):
        if font_name not in self.fonts.keys():
            return False
        self.font_name = font_name + '1'
        self.font_file = self.fonts[font_name]['font_file']
        self.font_size = self.fonts[font_name]['font_size']
        self.font_scan = self.fonts[font_name]['font_scan']
        print('font_name', self.font_name, 'font_size', self.font_size, 'font_scan', self.font_scan)
        return True

    def __init__(self, fonts, max_page_count=-1, page_width=21, page_height=29.7, font_name='楷体'):
        self.max_page_count = max_page_count
        self.fonts = fonts
        self.font_name = font_name + '1'
        self.font_file = self.fonts[font_name]['font_file']
        self.font_size = self.fonts[font_name]['font_size']
        self.font_scan = self.fonts[font_name]['font_scan']

        self.page_width = page_width
        self.page_height = page_height

        self.item_width = 1.5
        self.item_height = 1.5
        self.line_space = 0.2
        self.side_space = 1

        self.doc_width = self.page_width - self.side_space * 2
        self.doc_height = self.page_height - self.side_space * 2

        self.col_count = int(self.doc_width / self.item_width)
        self.row_count = int((self.doc_height + self.line_space) / (self.item_height + self.line_space))

        self.doc_width = self.col_count * self.item_width
        self.doc_height = self.row_count * (self.item_height + self.line_space) - self.line_space

        self.start_x = (self.page_width - self.doc_width) / 2 + self.item_width / 4
        self.start_y = (self.page_height - self.doc_height) / 2

        self.line_color = [colors.Color(199, 238, 206), colors.Color(199, 238, 206)]
        self.col_text_colors = ['lightgrey']  # 全部浅灰

        print('doc_width', self.doc_width, 'col_count', self.col_count)
        print('doc_height', self.doc_height, 'row_count', self.row_count)

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

    def _draw_item(self, _x, _y):
        y = self.page_height - _y - self.item_height
        self.canv.setStrokeColor(self.line_color[0])
        for col in range(0, self.col_count):
            x = _x + col * self.item_width
            item_width = self.item_width / 2
            self.canv.setDash([2, 2])
            _y = (y + self.item_height / 2) * cm
            self.canv.line(x * cm, _y, (x + item_width) * cm, _y)
            self.canv.setDash([])
            self.canv.rect(x * cm, y * cm, item_width * cm, self.item_height * cm)

    def draw_bank(self):
        self.canv.setStrokeColor(self.line_color[0])
        self.canv.setLineWidth(1)
        for row in range(0, self.row_count):
            x = self.start_x
            y = self.start_y + row * (self.item_height + self.line_space)
            self._draw_item(x, y)

    def _next(self):
        self.curr_index = self.curr_index + 1
        page_index = int(self.curr_index / self.col_count / self.row_count)
        if 0 <= self.max_page_count < page_index:
            return -1, -1

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
        if txt == '' or txt is None or row < 0:
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
        x += (self.item_width / 2 - txt_width / cm) / 2
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
