from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab import rl_config


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

    def __init__(self, fonts, show_pinyin=False, max_page_count=-1, page_width=21, page_height=29.7, font_name='楷体'):
        self.max_page_count = max_page_count
        self.fonts = fonts
        self.font_name = font_name + '1'
        cfg = self.fonts[font_name]
        self.font_file = cfg['font_file']
        self.font_size = cfg['font_size']
        self.font_scan = cfg['font_scan']
        self.grid_type = self.GRID_TYPE_MI

        self.page_width = page_width
        self.page_height = page_height

        self.item_width = 1.5
        self.item_height = 1.5
        self.line_space = 0.2
        self.side_space = 1
        self.line_pinyin = 0

        if "item_width" in cfg.keys():
            self.item_width = cfg["item_width"]

        if "item_height" in cfg.keys():
            self.item_height = cfg["item_height"]

        if "line_space" in cfg.keys():
            self.line_space = cfg["line_space"]

        if "side_space" in cfg.keys():
            self.side_space = cfg["side_space"]


        self.doc_width = self.page_width - self.side_space * 2
        self.doc_height = self.page_height - self.side_space * 2

        self.col_count = int(self.doc_width / self.item_width)

        self.show_pinyin = show_pinyin
        if self.show_pinyin:
            if "line_pinyin" in cfg.keys():
                self.line_pinyin = cfg["line_pinyin"]
            else:
                self.line_pinyin = 0.8
            self.row_count = int((self.doc_height + self.line_space) /
                                 (self.item_height + self.line_pinyin + self.line_space))
        else:
            self.line_pinyin = 0
            self.row_count = int((self.doc_height + self.line_space) /
                                 (self.item_height + self.line_pinyin + self.line_space))

        self.doc_width = self.col_count * self.item_width
        self.doc_height = self.row_count * (self.item_height + self.line_pinyin + self.line_space) - self.line_space

        self.start_x = (self.page_width - self.doc_width) / 2
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

    def _draw_fang(self, _x, _y):
        # 绘制每列的竖线
        y = self.page_height - _y - self.item_height
        self.canv.setDash([])
        self.canv.setStrokeColor(self.line_color[0])
        for col in range(0, self.col_count + 1):
            x = _x + col * self.item_width
            self.canv.line(x * cm, y * cm, x * cm, (y + self.item_height) * cm)

        # 绘制每行的外框
        x = _x
        y = self.page_height - _y - self.item_height
        self.canv.setDash([])
        self.canv.setStrokeColor(self.line_color[0])
        self.canv.rect(x * cm, y * cm, self.doc_width * cm, self.item_height * cm)

    def _draw_hui(self, _x, _y):
        # 绘制内框
        height = self.item_height * 0.7  # 该比例不一定正确。没有找到相关资料。该比例是量出来的。
        width = height * 0.618
        y = self.page_height - _y - (self.item_height - height) / 2
        for col in range(0, self.col_count):
            self.canv.setStrokeColor(self.line_color[1])
            x = _x + col * self.item_width + (self.item_width - width) / 2
            self.canv.rect(x * cm, y * cm, width * cm, -height * cm)

        self._draw_fang(_x, _y)

    def _draw_tian(self, _x, _y):
        # 绘制每格的中心水平虚线
        x = _x
        y = self.page_height - _y - self.item_height / 2
        self.canv.setDash([2, 2])
        self.canv.setStrokeColor(self.line_color[1])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        # 绘制每列中间的竖线
        y = self.page_height - _y
        self.canv.setDash([2, 2])
        self.canv.setStrokeColor(self.line_color[1])
        for index in range(0, self.col_count):
            x = _x + (index + 0.5) * self.item_width
            self.canv.line(x * cm, (y - self.item_height) * cm, x * cm, y * cm)

        self._draw_fang(_x, _y)

    def _draw_mi(self, _x, _y):
        # 绘制每格的中心水平虚线
        x = _x
        y = self.page_height - _y
        y -= self.item_height / 2
        self.canv.setDash([2, 2])
        self.canv.setStrokeColor(self.line_color[1])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)

        # 绘制每格的斜线
        y = self.page_height - _y - self.item_height
        for index in range(0, self.col_count):
            self.canv.setDash([2, 2])
            self.canv.setStrokeColor(self.line_color[1])
            x = _x + index * self.item_width
            self.canv.line(x * cm, y * cm, (x + self.item_width) * cm, (y + self.item_height) * cm)
            self.canv.line((x + self.item_width) * cm, y * cm, x * cm, (y + self.item_height) * cm)

        # 绘制每列中间的竖线
        y = self.page_height - _y
        self.canv.setDash([2, 2])
        self.canv.setStrokeColor(self.line_color[1])
        for index in range(0, self.col_count):
            x = _x + (index + 0.5) * self.item_width
            self.canv.line(x * cm, (y - self.item_height) * cm, x * cm, y * cm)

        self._draw_fang(_x, _y)

    def _draw_pinyin(self, _x, _y, line_height):
        x = _x
        y = self.page_height - _y
        self.canv.setDash([])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= line_height / 3
        self.canv.setDash([2, 2])
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= line_height / 3
        self.canv.line(x * cm, y * cm, (self.doc_width + x) * cm, y * cm)
        y -= line_height / 3
        self.canv.setDash([])

    def draw_bank(self):
        self.canv.setStrokeColor(self.line_color[0])
        self.canv.setLineWidth(1)
        for row in range(0, self.row_count):
            x = self.start_x
            y = self.start_y + row * (self.item_height + self.line_pinyin + self.line_space)
            if self.show_pinyin:
                self._draw_pinyin(x, y, self.line_pinyin)
                y += self.line_pinyin
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
        y = self.start_y + row * (self.item_height + self.line_pinyin + self.line_space)\
            + self.line_pinyin + self.item_height * self.font_scan
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
                if i + 1 >= self.col_count * repeat:
                    line_text.append('')
                else:
                    line_text.append(t)
        for t in line_text:
            self.draw_text(t)


if __name__ == '__main__':
    # for name in ['楷体', '华文楷体', '庞中华钢笔字体', '战加东硬笔楷书', '蝉羽真颜金戈', '田英章楷书']:
    for name in ['田英章楷书']:
        hanzi = HanZi(fonts=name)
        hanzi.create(name + '.pdf')
        hanzi.draw_mutilate_text('''
云蒸沧海，雨润桑田。阴阳世界，造化黎元。
羲农开辟，轩昊承传。魃凌涿鹿，熊奋阪泉。
四凶伏罪，群兽听宣。垂裳拱手，击壤欢颜。
挽弓射日，采石补天。巢由小隐，稷契大贤。

触峰贻患，治水移权。繇惟北面，舜竟南迁。

洪荒待考，虚诞连篇。聊将俊杰，尽作神仙。

桀纣多情，履发能征。每言失道，必曰倾城。

戮兄叔旦，述父武庚。败皆怙恶，成则彰名。

三王既殁，诸霸迭兴。七雄更勃，百战不宁。

起甘杀妇，羊忍啜羹。枉称顺逆，漫说纵横。

楚户秦俑，燕台赵坑。推诚赴会，转瞬渝盟。

役丁困死，戍卒求生。饱经丧乱，渴望升平。

始皇暴戾，赤帝刚柔。俱为一统，谁得千秋？

遂分郡县，稍褫公侯。豪侠饮恨，渔樵忘忧。

九畿旌旆，万里丝绸。计出帷幄，功归冕旒。

或逢外戚，空逞叛谋。秀堪应谶，莽固招尤。

汉廷何在？洛邑另修。往来阉宦，蹴踏清流。

魏晋受禅，陶虞蒙羞。蜀申炎祚，吴访夷洲。

瑜亮已逝，干戈且终。尘侵塞内，烟锁江东。

六朝斜月，五族飘风。尔登宝殿，朕坐囚笼。

投鞭踊跃，挥麈雍容。锋芒闪烁，血泪混融。

隋代至伟，齐州复同。寒窗苦读，进士荣封。

杨凋李继，周退唐隆。长明乃晦，极盛而穷。

怯谈藩镇，愁看深宫。篡臣交替，僭主相攻。

稚童徒泣，点检难防。惯冲营阵，巧取庙堂。

力除前弊，反致后殃。但吞闽岭，未定朔方。

虽繁市肆，屡怅边疆。凄惶离汴，逸乐居杭。

欺心奸佞，涅背忠良。仍遭德祐，敢忆靖康？

狼奔沃野，龙没汪洋。怒声幽咽，浩气苍凉。

匹夫举义，衲子安邦。勋贵并翦，恩威远航。

花鼓久唱，胡弦又弹。八旗猛烈，十室隳残。

细删坟典，强改衣冠。扰绥奴婢，震慑戎蛮。

欧师美旅，锐炮坚船。惕兢揖盗，慷慨和蕃。

昼消积雪，夜涌狂澜。金銮骤废，火凤频燃。

秣陵惨怖，缅甸辛酸。粟枪驱寇，镰斧劈山。

凿穿愚昧，扫净冥顽。红霞普照，碧宇偕攀！

先哲所知，今我之资。卷丰旨博，意畅魂驰。

白马诡辩，青牛玄思。商韩利害，孔孟孝慈。

兵家有策，墨者无私。观星邹衍，问稼樊迟。

斩蛟驭鹤，跨象乘狮。法休妄悟，戒可恒持。

真佛劝善，伪僧媚时。常存正念，莫祷淫祠。

随缘似懒，格物若痴。勉探精粹，渐却瑕疵。

嬴政焚书，刘彻尊儒。独裁专制，异轨殊途。

仆非轻贱，君自寡孤。澹然朱紫，妙矣莼鲈。

奉亲首责，报国宏图。睦友以信，悦妻如初。

爱当掷果，贞只还珠。女宜立业，男亦入厨。

礼须微薄，仪忌粗疏。禁奢从俭，守洁去污。

理争尺寸，财舍锱铢。临危谨慎，闻诟糊途。
华夏巍峨，文章耸峙。窥测豹斑，步趋麟趾。

断竹鸣歌，结绳纪事。甲骨撰辞，鼎碑刻字。

嗟咏饥劳，颂吟祭祀。藉此抒怀，因其阐志。

荷锄展喉，抛笏戟指。抱蕙兰芬，吐蔷薇刺。

骚屈哀民，漆庄避仕。盲岂误编，腐犹著史。

萧瑟毫端，扶摇胸次。倚案抚膺，破霄振翅。

瑶琴古韵，牙板新腔。濯莲沁酒，漱玉含霜。

诗宗老杜，词祖重光。律工沈宋，艺让苏黄。

桃源遗迹，柳岸余觞。艳撩蝶舞，醉激鹰扬。

曲喧茶社，赋售椒房。俚音跌宕，骈句铿锵。

松龄话鬼，芹圃怜香。病魔噬体，呓语牵肠。

谦益节妓，晓岚幸倡。笔加脂粉，愧及膏肓。

胜境欲描，旧籍易抄。熟谙脉络，勿惑皮毛。

行间璀璨，灯下寂寥。少年涉涧，壮岁弄潮。

请呈朋辈，共励儿曹。''')
        hanzi.close()
