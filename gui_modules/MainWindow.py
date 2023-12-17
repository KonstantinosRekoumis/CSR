from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QStackedLayout, QMainWindow)
from PySide6.QtWidgets import (QWidget, QFileDialog)

import modules.io.IO as IO
from gui_modules.PlotRenderWidget import DiagramPanel
from gui_modules.TableWidget import TablesPanel
from gui_modules.ToolBarActions import ExitAction, LoadAction, SaveAction, AboutAction
from modules.utilities.logger import Logger
from modules.datahandling.datalogger import DataLogger
    
class AuxWindow(QWidget):
    """
    Class for all the necessary auxiliary windows
    """

    def __init__(self, widgets: list[QWidget], title):
        super().__init__()
        layout = QVBoxLayout()
        [layout.addWidget(widget) for widget in widgets]
        self.setWindowTitle(title)
        self.setLayout(layout)


class LoadFileDialog(QFileDialog):
    """
    Class to Graphically Load the Project. 
    """

    def __init__(self, parent=None, mode=0):
        """
        Load/Save File Dialog:
        mode = 0 for Load
        mode = 1 for Save
        """
        title = 'Load' if mode == 0 else "Save"
        super().__init__(parent, title, '.', "Project Files (*.json)")
        self.setOption(self.Option.DontUseNativeDialog, True)


class MainWindow(QMainWindow):
    def __init__(self,title: str, parent=None):
        super().__init__(parent)
        # Title update
        self.setWindowTitle(f'SDA MSD ver.:0.1 ')
        # Initialize ship and data_logger variables
        self.ship = None 
        self.data_logger = None
        # Create a central Widget to attach everything on to
        self.canvas = QWidget()
        self.setCentralWidget(self.canvas)
        # Create Auxiliary windows
        self.about_win = AuxWindow([QLabel(title, alignment=Qt.AlignCenter)], "About")
        self.load_save_window(0)
        # Main Menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu('File')
        self.menu_file.addAction(ExitAction(self))
        self.menu_file.addAction(LoadAction(self, partial(self.load_save_window, 0)))
        self.menu_file.addAction(SaveAction(self, partial(self.load_save_window, 1)))
        # self.menu_about = self.menu.addMenu('About')
        self.menu.addAction(
            AboutAction(self, partial(self.show_new_window, self.about_win)))
        # Widget init
        self.text = QLabel(title,alignment=Qt.AlignCenter)
        self.table = TablesPanel(self.data_logger, self)
        self.graph = DiagramPanel(self.ship, self,)
        self.button = QPushButton('Start')
        # Layout
        self.displayLayout = QStackedLayout()
        self.displayLayout.addWidget(self.text)
        self.displayLayout.addWidget(self.table)
        self.displayLayout.addWidget(self.graph)
        # Central layout
        layout = QVBoxLayout(self.canvas)
        layout.addLayout(self.displayLayout)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.button.clicked.connect(self.say_hello)
        # self.fig.set_canvas(self.canvas)
        # self._ax = self.canvas.figure.add_subplot()
        # self._ax = ax

    def say_hello(self):
        Logger.success("hmmm....")
        if self.displayLayout.currentIndex() == 1:
            self.displayLayout.setCurrentIndex(2)
        elif self.displayLayout.currentIndex() == 0:
            self.displayLayout.setCurrentIndex(1)
        else:
            self.displayLayout.setCurrentIndex(0)

    def show_new_window(self, target):
        if not target.isVisible():
            target.show()

    def load_save_window(self, mode):
        if mode == 0:
            data = LoadFileDialog(mode=mode).getOpenFileName(self, 'Load', '.', "Project Files (*.json)")
            if data[0] != '':
                if data[0][-5:] == '.json':
                    self.ship = IO.load_ship(data[0])
                    self.data_logger = DataLogger(self.ship)
                    self.data_logger.create_tabular_data()
                    self.setWindowTitle(f'SDA MSD ver.:0.1 {data[0]}')
                    print(self.ship.LBP)
                else:
                    Logger.warning('Ship data files are .json files')
            elif data[0] == '' and self.ship is None:
                #TODO: Start the program without loading any ship and only after
                #loading one render the UI except the menu bars
                Logger.error(" The program can not execute without inputing a ship envelope!")
        elif mode == 1:
            data = LoadFileDialog(mode=mode).getOpenFileName(self, "Save", '.', "Project Files (*.json)")
            if data[0] != '':
                IO.ship_save(self.ship, data[0][:-5] + '_new.json')
