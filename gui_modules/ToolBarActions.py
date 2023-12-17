import sys
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt


class ExitAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText('Exit')
        self.triggered.connect(sys.exit)
        self.setShortcut(QKeySequence(Qt.ALT | Qt.Key_Q))


class LoadAction(QAction):
    def __init__(self, parent, f):
        super().__init__(parent)
        self.setText('Load File')
        self.triggered.connect(f)
        self.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_O))


class SaveAction(QAction):
    def __init__(self, parent, f):
        super().__init__(parent)
        self.setText('Save File')
        self.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_S))
        self.triggered.connect(f)


class AboutAction(QAction):
    def __init__(self, parent, f):
        # f is the function to trigger the new window
        super().__init__(parent)
        self.setText('About')
        self.triggered.connect(f)
