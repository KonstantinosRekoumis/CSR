# -_-
# #################################
'''
Structural Calculator for Bulk Carriers 
Courtesy of Navarx0s and his st0los

--- GUI MODE ---

STUDIES HSM and BSP conditions at midships
'''
# #################################
#_____ IMPORTS _____
# import ezdxf #to be installed 

#_____ CALLS _______
import os, sys
import modules.classes as cl
from modules.constants import RHO_S
import modules.physics as phzx
import modules.rules as csr
import modules.render as rnr
import modules.IO as IO
from modules.utilities import c_info,_TITLE_,_RESET_, c_success

from PySide6 import QtCore, QtWidgets, QtGui
TITLE = (
        "   ____  ____    _      __  __ ____  ____    \n"
        '  / ___||  _ \  / \    |  \/  / ___||  _ \\  \n'
        '  \___ \| | | |/ _ \   | |\/| \___ \| | | |  \n'
        '   ___) | |_| / ___ \  | |  | |___) | |_| |  \n'
        '  |____/|____/_/   \_\ |_|  |_|____/|____/   \n'
        '--- SHIP DESIGN ASSIGNMENT MIDSHIP DESIGN ---\n'
        '    ---- 2022, Rekoumis Konstantinos ----    \n\n'
        '  ### All Rights Reserved - MIT Lisence ###  \n'
        'This code is developed to aid the design of the \n'
        'principal strength members of a ship\'s Midship. \n'
        'For the time being is developed for Bulk Carriers,\n'
        ' under Common Structural Rules 2022 Version.\n'
        )

class myWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        self.text = QtWidgets.QLabel(TITLE,alignment=QtCore.Qt.AlignCenter)
        # self.text.setTextFormat(QtCore.Qt.MarkdownText)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = myWidget()
    widget.resize(800,450)
    widget.show()

    sys.exit(app.exec())
