import os
import sys

from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor, QPaintEvent, QPainter, QBrush, QImage, QScreen
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, QSystemTrayIcon

from backend.stat import check_newest
from events import events
from ui.HanZi import UiHanZi
from ui.Number import UiNumber
from ui.PinYin import UiPinYin
from version import version

if getattr(sys, 'frozen', False):  # 是否Bundle Resource
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
font_path = os.path.join(base_path, 'fonts')


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
    def __init__(self, screen: QScreen):
        super().__init__(parent=None)
        events.signal_check_newest.connect(self.on_check_newest)
        events.signal_pop_message.connect(self.on_pop_message)
        self.tray = QSystemTrayIcon(self)

        self.setWindowTitle("字帖生成器 {}".format(version["curr"]))
        self.icon = load_icon('app.png')
        self.setWindowIcon(self.icon)
        self.screen = screen
        self.root_layout = QHBoxLayout(self)

        # 初始化右侧布局
        self.right_side = QStackedLayout()
        self.pinyin = UiPinYin(font_path)
        self.right_side.addWidget(self.pinyin)
        self.hanzi = UiHanZi(font_path)
        self.right_side.addWidget(self.hanzi)
        self.number = UiNumber(font_path)
        self.right_side.addWidget(self.number)

        # 初始化左侧布局：功能按钮
        self.left_side = QVBoxLayout()
        self.left_side.setSpacing(0)
        self.left_side.setContentsMargins(0, 0, 0, 0)
        self.left_side.setAlignment(Qt.AlignTop)
        self.btn_pinyin = MyButton('  拼音  ', 0, self.right_side, "pin")
        self.left_side.addWidget(self.btn_pinyin)
        self.btn_hanzi = MyButton('  汉字  ', 1, self.right_side, "han")
        self.left_side.addWidget(self.btn_hanzi)
        self.btn_number = MyButton('  数字  ', 2, self.right_side, "number")
        self.left_side.addWidget(self.btn_number)
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

        # Fixme:直接调用的话会因为窗口大小不对而不居中。
        self.t = QTimer()
        self.t.timeout.connect(self.center)
        self.t.start(10)
        check_newest()
        events.signal_pop_message.emit("直接调用的话会因为窗口大小不对而不居中。")

    def center(self):
        self.t.stop()
        screen = self.screen.availableSize()
        rect = self.geometry()
        self.move(int((screen.width() - rect.width()) / 2),
                  int((screen.height() - rect.height()) / 2))

    @staticmethod
    def on_check_newest(new_version):
        events.signal_pop_message("检测到新版本：\n{}: {}".format(
            new_version['curr'],
            new_version['history'][new_version['curr']])
        )
        # TODO：执行升级

    def on_pop_message(self, msg):
        self.tray.show()
        self.tray.showMessage("字帖", msg, self.icon)
        self.tray.hide()
