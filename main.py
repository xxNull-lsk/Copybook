import sys
import os
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QIcon, QFocusEvent, QPalette, QColor, QPaintEvent, QPainter, QBrush, QPolygonF, QImage
from PyQt5.QtWidgets import QPushButton, QDesktopWidget, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, \
    QApplication, QRadioButton

from ui.HanZi import UiHanZi
from ui.PinYin import UiPinYin

if getattr(sys, 'frozen', False):  # 是否Bundle Resource
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
font_path = os.path.join(base_path, 'fonts')

version = {
    "curr": "0.0.4",
    "history": {
        "0.0.1": "实现基本的拼音字帖和汉字字帖",
        "0.0.2": "1. 支持方格\n"
                 "2. 支持回宫格",
        "0.0.3": "1. 支持预览\n"
                 "2. 优化汉字字帖生成逻辑",
        "0.0.4": "优化界面"
    }
}


color_left_side = QColor(210, 210, 210)
color_left_high = QColor(133, 133, 133)


def load_icon(name):
    return QIcon(os.path.join(base_path, "res", name))


def load_image(name):
    return QImage(os.path.join(base_path, "res", name))


class MyButton(QPushButton):
    def __init__(self, txt, page_index, stacked_layout: QStackedLayout, icon_name):
        super().__init__(txt)
        self.icon_name = icon_name
        self.stacked_layout = stacked_layout
        self.page_index = page_index
        self.setFixedHeight(48)
        self.setFixedWidth(128)
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.stacked_layout.setCurrentIndex(self.page_index)

    def paintEvent(self, e: QPaintEvent):
        p = QPainter()
        p.begin(self)
        p.setRenderHint(p.Antialiasing)
        rect = self.rect()
        icon_name = self.icon_name
        if self.page_index == self.stacked_layout.currentIndex():
            p.fillRect(rect, QBrush(color_left_high))
            icon_name += "1"

        fm = p.fontMetrics()
        text_width = fm.width(self.text())
        img = load_image(icon_name + '.png')
        w = img.width()
        h = img.height()
        rect_img = QRect(
            int(rect.left() + (rect.width() - text_width - w) / 2),
            int(rect.top() + (rect.height() - h) / 2),
            w,
            h
        )
        p.drawImage(rect_img, img)
        rect = self.rect()
        rect.moveLeft(int(w / 2))
        p.drawText(rect, Qt.AlignCenter, self.text())
        p.end()


class MyMainWindow(QWidget):
    def __init__(self):
        super().__init__(parent=QDesktopWidget())
        self.resize(360, 360)
        self.setWindowTitle("字帖生成器 {}".format(version["curr"]))
        self.setWindowIcon(load_icon('app.png'))

        self.root_layout = QHBoxLayout(self)

        # 初始化右侧布局
        self.right_side = QStackedLayout()
        self.pinyin = UiPinYin(font_path)
        self.right_side.addWidget(self.pinyin)
        self.hanzi = UiHanZi(font_path)
        self.right_side.addWidget(self.hanzi)

        # 初始化左侧布局：功能按钮
        self.left_side = QVBoxLayout()
        self.left_side.setSpacing(0)
        self.left_side.setContentsMargins(0, 0, 0, 0)
        self.left_side.setAlignment(Qt.AlignTop)
        self.btn_pinyin = MyButton('  拼音  ', 0, self.right_side, "pin")
        self.left_side.addWidget(self.btn_pinyin)
        self.btn_hanzi = MyButton('  汉字  ', 1, self.right_side, "han")
        self.left_side.addWidget(self.btn_hanzi)
        left = QWidget()
        p = QPalette()
        p.setColor(QPalette.Background, color_left_side)
        left.setPalette(p)
        left.setAutoFillBackground(True)
        left.setLayout(self.left_side)

        # 初始化整体布局
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.addWidget(left)
        self.root_layout.addLayout(self.right_side)

        # 显示窗口
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        print(version["curr"])
        return
    app = QApplication(sys.argv)
    ex = MyMainWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
