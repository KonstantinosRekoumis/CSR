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

# %%
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # main()
    widget = win.MainWindow(TITLE)
    # widget = QtWidgets.QFileDialog()
    widget.resize(1280, 720)    
    widget.show()

    sys.exit(app.exec())