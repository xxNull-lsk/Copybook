import json
import sys
from version import version


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-v':
            print(version["curr"])
            return
        elif sys.argv[1] == '-i':
            print(json.dumps(version, ensure_ascii=False))
            return
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from main_window import MyMainWindow
    ex = MyMainWindow(app.primaryScreen())
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
