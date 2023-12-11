from functools import partial
from typing import Optional
import PySide6.QtCore

from modules.baseclass.ship import Ship
import modules.render as rnr
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import enum

class RendererS(enum.Enum):
    OutlinePlot = rnr.lines_plot
    BlocksPlot  = rnr.block_plot
    PressPlot   = rnr.pressure_plot
    ThickPlot   = partial(rnr.contour_plot, key = 'thickness')
    SpacePlot   = partial(rnr.contour_plot, key = 'spacing')
    MatPlot     = partial(rnr.contour_plot, key = 'material')
    TagPlot     = partial(rnr.contour_plot, key = 'tag')
    IdPlot      = partial(rnr.contour_plot, key = 'id')

TEXTS = {
'Outline Plot' : RendererS.OutlinePlot, 
'Blocks Plot' : RendererS.BlocksPlot, 
'Pressure Plot' : RendererS.PressPlot, 
'Thickness Plot' : RendererS.ThickPlot.value, 
'Stiffener Spacing Plot' : RendererS.SpacePlot.value, 
'Plating Material Plot' : RendererS.MatPlot.value, 
'Plating Tag Plot' : RendererS.TagPlot.value, 
'Plating Id Plot' : RendererS.IdPlot.value 
}
class DiagramPanel(QWidget):
    '''
    The panel to be imported in the main window that will also handle the
    transition between the different plots 
    '''
    def __init__(self, ship : Ship, parent: QWidget | None = ..., **kwargs) -> None:
        super().__init__(parent)
        self.ship = ship
        # Instantiate the Dropdown menu
        self.dropDown = QComboBox()
        self.dropDown.addItems(TEXTS.keys())
        self.dropDown.currentTextChanged.connect(self.update_plot)
        self.fig = Figure(figsize=(6.4, 4.8))
        self.fig_canvas = FigureCanvas(self.fig)
        # self.fig_canvas = MplCanvas(self)

        layout = QVBoxLayout()
        layout.addWidget(self.fig_canvas)
        layout.addWidget(self.dropDown)
        self.setLayout(layout)
        self.update_plot('Outline Plot')

    
    def update_plot(self, text, **kwargs):
        print(text)
        plot = TEXTS[text]
        # Reset the figure 
        self.fig.clear()
        self._ax = self.fig_canvas.figure.add_subplot()
        plot(self.ship, fig = self.fig, ax = self._ax, **kwargs)
        self.fig_canvas.draw()




