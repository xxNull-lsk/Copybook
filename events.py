from PyQt5.QtCore import QObject, pyqtSignal


class Events(QObject):
    signal_check_newest = pyqtSignal(dict)
    signal_pop_message = pyqtSignal(str)


events = Events()
