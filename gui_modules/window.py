import sys
from functools import partial
from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QStackedLayout,QMainWindow)
from PySide6.QtWidgets import (QTableWidget,QTableWidgetItem)
from PySide6.QtWidgets import (QWidget,QItemDelegate,QFileDialog)
from PySide6.QtCore import Qt , Slot
from PySide6.QtGui import QAction
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
import modules.classes as cls
import modules.IO as IO
import modules.render as rnr
from gui_modules.ToolBarActions import ExitAction, LoadAction, SaveAction, AboutAction
from modules.utilities import c_info,_TITLE_,_RESET_, c_success, c_error, c_warn

class dataManager:
    def __init__(self,data,header):
        self.header = header
        self.data = data
    def say_hello(self):
        return self.data, self.header
    
class AuxWindow(QWidget):
    """
    Class for all the necessary auxiliary windows
    """
    def __init__(self,widgets:list[QWidget]):
        super().__init__()
        layout = QVBoxLayout()
        [layout.addWidget(widget) for widget in widgets]
        self.setLayout(layout)

class LoadFileDialog(QFileDialog):
    """
    Class to Graphically Load the Project
    """
    def __init__(self,parent=None,mode=0):
        """
        Load/Save File Dialog:
        mode = 0 for Load
        mode = 1 for Save
        """
        title = 'Load' if mode == 0 else "Save"
        super().__init__(parent,title,'.',"Project Files (*.json)")
        self.setOption(self.Option.DontUseNativeDialog, True)
        self.setWindowTitle(title)




class MainWindow(QMainWindow):
    def __init__(self,title,dataManager: dataManager, parent=None):
        super().__init__(parent)
        path = r"D:\Python Projects\CSR\final.json" #temporary
        self.setWindowTitle(f'SDA MSD ver.:0.1 {path}')
        self.ship = None # Initial Value
        # Create a central Widget to attach everything on to
        self.canvas = QWidget()
        self.setCentralWidget(self.canvas)
        # Create Auxiliary windows
        self.about_win = AuxWindow([QLabel(title,alignment=Qt.AlignCenter)])
        self.load_save_window(0)
        # Main Menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu('File')
        self.menu_file.addAction(ExitAction(self))
        self.menu_file.addAction(LoadAction(self,partial(self.load_save_window,0)))
        self.menu_file.addAction(SaveAction(self,partial(self.load_save_window,1))) 
        self.menu_about = self.menu.addMenu('About')
        self.menu_about.addAction(
            AboutAction(self,partial(self.show_new_window,self.about_win)))


        self.dataManager = dataManager
        # Widget init
        self.text = QLabel(title,alignment=Qt.AlignCenter)
        self.table = table(*self.dataManager.say_hello())
        # self.fig = Figure(figsize=(8,4))
        self.fig,self.ax = rnr.lines_plot(self.ship,show=False)
        self.fig_canvas = FigureCanvas(self.fig)
        
        self.button = QPushButton('Start')
        # Layout
        self.displayLayout = QStackedLayout()
        self.displayLayout.addWidget(self.text)
        self.displayLayout.addWidget(self.table)
        self.displayLayout.addWidget(self.fig_canvas)
        # Central layout
        layout = QVBoxLayout(self.canvas)
        layout.addLayout(self.displayLayout)
        layout.addWidget(self.button)
        self.fig_canvas.draw()
        self.setLayout(layout)
        self.button.clicked.connect(self.say_hello)
        # self.fig.set_canvas(self.canvas)
        # self._ax = self.canvas.figure.add_subplot()
        # self._ax = ax
    def say_hello(self):
        c_success("hmmm....")
        if self.displayLayout.currentIndex() == 1:
            self.displayLayout.setCurrentIndex(2)
        elif self.displayLayout.currentIndex() == 0:
            self.table.populate_table(*self.dataManager.say_hello())
            self.displayLayout.setCurrentIndex(1)
        else:
            self.displayLayout.setCurrentIndex(0)

    def show_new_window(self,target):
        if not target.isVisible():
            target.show()
    def load_save_window(self,mode):
        if mode == 0:
            data = LoadFileDialog(mode=mode).getOpenFileName(self,'Load','.',"Project Files (*.json)")
            if data[0] != '':
                if data[0][-5:] == '.json':
                    self.ship = IO.load_ship(data[0])
                    print(self.ship.LBP)
                else:
                    c_warn('Ship data files are .json files')
        elif mode == 1:
            data = LoadFileDialog(mode=mode).getOpenFileName(self,"Save",'.',"Project Files (*.json)")
            if data[0] != '':
                IO.ship_save(self.ship ,data[0][:-5]+'_new.json')



class ShipParticLayout(QStackedLayout):
    """
    Create the panel of  ship particulars
    """
    def __init__(self,ship :cls.ship,parent=None):
        super(ShipParticLayout,self).__init__(parent)
        self.ship = ship



class AlignDelegate(QItemDelegate):
    # https://stackoverflow.com/questions/46772790/pyside-align-text-in-a-table-cells
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        # option.
        QItemDelegate.paint(self, painter, option, index)

class table(QTableWidget):
    def __init__(self,data,header,parent=None):
        super(table,self).__init__(parent)
        self.horizontalHeader()
        self.populate_table(data,header)

    def populate_table(self,data,header):
        self.setRowCount((len(data)))
        self.setColumnCount(len(data[0]))
        self.setHorizontalHeaderLabels(header)
        for i, cell in enumerate(data):
            if len(cell) == self.columnCount():
                [self.setItem(i,j,QTableWidgetItem(str(item))) for j, item in enumerate(cell)]
            else:
                c_error("The data provided are trash retard")
                print(data)
                print(self.columnCount())
                break
        self.setItemDelegate(AlignDelegate())



