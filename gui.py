import sys

from PySide6 import QtWidgets

import gui_modules.MainWindow as win
import modules.io.IO as IO
from modules.io.datacell import DataCell

TITLE = r"""
   ____  ____    _      __  __ ____  ____    
  / ___||  _ \  / \    |  \/  / ___||  _ \  
  \___ \| | | |/ _ \   | |\/| \___ \| | | |  
   ___) | |_| / ___ \  | |  | |___) | |_| |  
  |____/|____/_/   \_\ |_|  |_|____/|____/   
--- SHIP DESIGN ASSIGNMENT MIDSHIP DESIGN ---
    ---- 2022, Rekoumis Konstantinos ----    
  ###           MIT License            ###  
This code is developed to aid the design of the 
principal strength members of a ship\'s Midship. 
For the time being is developed for Bulk Carriers,
under Common Structural Rules 2022 Version.
"""

header = ["id", 'Length', 'spacing', 'stiffener']
data = [[0, 12, 2.5, 'Tau'],
        [0, 13, 2.7, 'G'], ]


ship = IO.load_ship('out/final.json')
data, header = DataCell(ship.stiff_plates[0]).get_data()
tmp = [DataCell(i).get_data(getHeader=False) for i in ship.stiff_plates]
data = [data, *tmp]
Dm = win.DataManager(data, header)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = win.MainWindow(TITLE, Dm)
    widget.resize(1280, 720)
    widget.show()

    sys.exit(app.exec())