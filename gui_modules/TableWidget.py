from typing import Optional
from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QItemDelegate)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QComboBox, QStackedLayout)
from PySide6.QtCore import Qt
from modules.utilities import Logger
from modules.datahandling.datalogger import DataLogger


class AlignDelegate(QItemDelegate):
    # https://stackoverflow.com/questions/46772790/pyside-align-text-in-a-table-cells
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        # option.
        QItemDelegate.paint(self, painter, option, index)

class TablesPanel(QWidget):
    def __init__(self, data_logger: DataLogger, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        self.data_logger = data_logger
        # multiple tables instantiation
        # self.Press_Table = Table(self.data_logger.Press_D, self.data_logger.Press_Header )
        self.Plate_Table = Table(self.data_logger.Plate_D, self.data_logger.Plate_Header )
        self.Stiff_Table = Table(self.data_logger.Stiff_D, self.data_logger.Stiff_Header )
        self.St_Pl_Table = Table(self.data_logger.St_Pl_D, self.data_logger.St_Pl_Header )
        self.PrimS_Table = Table(self.data_logger.PrimS_D, self.data_logger.PrimS_Header )
        main_layout = QVBoxLayout()
        self.table_layout = QStackedLayout()
        # self.table_layout.addWidget(self.Press_Table)
        self.table_layout.addWidget(self.Plate_Table)
        self.table_layout.addWidget(self.Stiff_Table)
        self.table_layout.addWidget(self.St_Pl_Table)
        self.table_layout.addWidget(self.PrimS_Table)
        self.panels_names = [
                            # 'Pressures Table',
                            'Plating Table',
                            'Stiffeners Table',
                            'Stiffened Plates Table',
                            'Ordinary Section Table']
        self.dropDown = QComboBox()
        self.dropDown.addItems(self.panels_names)
        self.dropDown.currentIndexChanged.connect(self.switch_table)
        main_layout.addLayout(self.table_layout)
        main_layout.addWidget(self.dropDown)
        self.setLayout(main_layout)

    def switch_table(self, index: int):
        self.table_layout.setCurrentIndex(index)

class Table(QTableWidget):
    def __init__(self,data,header,parent=None):
        super(Table,self).__init__(parent)
        self.horizontalHeader()
        self.populate_table(data,header)

    def populate_table(self,data,header):
        self.setRowCount((len(data)))
        self.setColumnCount(len(data[1]))
        self.setHorizontalHeaderLabels(header)
        for i, cell in enumerate(data):
            if isinstance(cell, list) or isinstance(cell, tuple):
                [self.setItem(i,j,QTableWidgetItem(str(item))) for j, item in enumerate(cell)]
            elif isinstance(cell, str):
                self.setItem(i,0,QTableWidgetItem(cell))
        self.setItemDelegate(AlignDelegate())