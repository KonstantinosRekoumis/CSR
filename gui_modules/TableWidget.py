from PySide6.QtWidgets import (QTableWidget,QTableWidgetItem,QItemDelegate)
from PySide6.QtCore import Qt
from modules.utils.logger import Logger


class AlignDelegate(QItemDelegate):
    # https://stackoverflow.com/questions/46772790/pyside-align-text-in-a-table-cells
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        # option.
        QItemDelegate.paint(self, painter, option, index)

class Table(QTableWidget):
    def __init__(self,data,header,parent=None):
        super(Table,self).__init__(parent)
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
                Logger.warning("The data provided are trash retard")
                print(data)
                print(self.columnCount())
                break
        self.setItemDelegate(AlignDelegate())