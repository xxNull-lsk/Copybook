from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm


# 定义注册中文字体字库的方法，此处默认为微软雅黑，
# 字体库文件的存放路径为当前目录，所以直接使用文件名
def set_font(canv, size, font_name='msyh', font_file='msyh.ttc'):
    pdfmetrics.registerFont(TTFont(font_name, font_file))
    canv.setFont(font_name, size)


page_width = 21
page_height = 29.7
start_x = 0.8
start_y = 1.5

doc_width = page_width - start_x * 2
doc_height = page_height - start_y * 2

col_count = 5
col_width = doc_width / col_count
print('doc_width', doc_width, 'col_width', col_width)

line_space = 0.6
line_height = 1.5
line_count = int((doc_height + line_space) / (line_height + line_space))
print('line_count', line_count, (doc_height + line_space) / (line_height + line_space))


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
    canv.setStrokeColor('lightgreen')
    canv.setLineWidth(1)
    for row in range(0, line_count):
        x = start_x
        y = start_y + row * (line_height + line_space)
        draw_4_line(canv, x, y)


def draw_text(canv, row, col, txt):
    x = start_x + col * col_width
    y = page_height - (start_y + row * (line_height + line_space))
    txt_width = canv.stringWidth(txt)
    x += (col_width - txt_width / cm) / 2
    canv.drawString(x * cm, y * cm, txt)


def draw_mutilate_text(canv, txt):
    for index, t in enumerate(txt):
        row = int(index / col_count)
        col = int(index % col_count)
        draw_text(canv, row, col, t)


def main():
    # 定义PDF文件存放文件名
    pdf_path = "test.pdf"
    # 建立文件
    canv = canvas.Canvas(pdf_path, pagesize=(page_width * cm, page_height * cm))
    draw_bank(canv)
    txt = ['zheng', 'zhuang', 'xia', 'man', 'mai', 'ni', 'wo']
    draw_mutilate_text(canv, txt)
    # 完成证件PDF一页
    canv.showPage()
    # 保存PDF文件
    canv.save()
    return
    # 设置字体及字号
    set_font(canv, 16)
    # 写入证件的相关文字信息其位置为x*cm,y*cm
    x = 1
    y = 28
    xp = 8
    yp = 20
    info = "测试"
    WATERMARK_TXT = "这是一个水印"
    width = 21
    # 15 181 90
    canv.setStrokeColor('lightgreen')
    canv.setLineWidth(1)
    canv.line(x * cm, y * cm, (width - x) * cm, y * cm)
    y += 0.5
    canv.setDash([2, 2])
    canv.line(x * cm, y * cm, (width - x) * cm, y * cm)
    y += 0.5
    canv.setDash([4, 4])
    canv.line(x * cm, y * cm, (width - x) * cm, y * cm)
    canv.setFillColor("lightgreen")
    canv.drawString(x * cm, y * cm, info)
    # 写入证件的照片信息其位置为xp*cm,yp*cm
    canv.drawImage('./photo.jpg', xp * cm, yp * cm)
    # 设置要添加的水印文字颜色及透明度
    canv.setFillColorRGB(180, 180, 180, alpha=0.3)
    # 写入水印文字，这里将水印文字放在证件照上
    set_font(canv, 7)
    canv.drawString(xp * cm, yp * cm + 0.5 * cm, WATERMARK_TXT)
    # 完成证件PDF一页
    canv.showPage()
    # 保存PDF文件
    canv.save()


if __name__ == '__main__':
    main()
