from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm


class PinYin:
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
    col_text_colors = ['lightgrey']  # 全部浅灰
    canv = None
    curr_page = -1
    curr_index = -1

    def __init__(self, page_width=21, page_height=29.7, start_x=0.8, start_y=1.5, col_count=5):
        self.font_name = '汉语拼音'
        self.font_file = 'fonts/汉语拼音.ttf'
        self.font_size = 28
        self.font_scan = 0.67

        self.page_width = page_width
        self.page_height = page_height
        self.start_x = start_x
        self.start_y = start_y

        self.doc_width = self.page_width - self.start_x * 2
        self.doc_height = self.page_height - self.start_y * 2

        self.col_count = col_count
        self.col_width = self.doc_width / self.col_count

        self.line_space = 0.6
        self.line_height = 1.5
        self.line_color = 'lightgreen'
        self.line_count = int((self.doc_height + self.line_space) / (self.line_height + self.line_space))
        self.col_text_colors = ['lightgrey']  # 全部浅灰

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
        pdfmetrics.registerFont(TTFont(self.font_name, self.font_file))
        self.canv.setFont(self.font_name, size)

    def _draw_4_line(self, _x, _y):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.line_height / 3
        self.canv.setDash([2, 2])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.line_height / 3
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= self.line_height / 3
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        for index in range(0, self.col_count + 1):
            x = _x + index * self.col_width
            self.canv.line(x * cm, y * cm, x * cm, (y + self.line_height) * cm)

    def draw_bank(self):
        self.canv.setStrokeColor(self.line_color)
        self.canv.setLineWidth(1)
        for row in range(0, self.line_count):
            x = self.start_x
            y = self.start_y + row * (self.line_height + self.line_space)
            self._draw_4_line(x, y)

    def _next(self):
        self.curr_index = self.curr_index + 1
        page_index = int(self.curr_index / self.col_count / self.line_count)
        if self.curr_page != page_index:
            if self.curr_page != -1:
                self.canv.showPage()
            # 设置字体及字号
            self._set_font(self.font_size)
            self.draw_bank()
            self.curr_page = page_index

        row = int(self.curr_index / self.col_count) - self.line_count * self.curr_page
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

        x = self.start_x + col * self.col_width
        y = self.start_y + row * (self.line_height + self.line_space) + self.line_height * self.font_scan
        txt_width = self.canv.stringWidth(txt)
        x += (self.col_width - txt_width / cm) / 2
        y = self.page_height - y  # 转换坐标系，右上角坐标系，转换成左下角
        self.canv.drawString(x * cm, y * cm, txt)

    def draw_mutilate_text(self, txt):
        for t in txt:
            self.draw_text(t)

    def draw_text_pre_line(self, txt, repeat=0.0):
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
