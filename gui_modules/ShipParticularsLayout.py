from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QStackedLayout)
import modules.classes as cls

class ShipParticLayout(QStackedLayout):
    """
    Create the panel of  ship particulars.
    There should be the following elements:
        - Ship Basic Particulars Table\n
        - Table of the defined plates
        - Table of the defined Volumes\\blocks
        - Figure of the defined plates id
        - Figure of the defined plates tag
        - Figure of the defined Volumes\\blocks
        - Figure of the MidShip Section
    """
    def __init__(self,ship :cls.ship,parent=None):
        super(ShipParticLayout,self).__init__(parent)
        self.ship = ship