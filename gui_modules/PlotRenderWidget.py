from functools import partial
from typing import Optional
import PySide6.QtCore

import modules.classes as cls
import modules.render as rnr
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import enum

class RendererS(enum.Enum):
    OutlinePlot = rnr.lines_plot
    BlocksPlot  = rnr.block_plot
    PressPlot   = rnr.pressure_plot
    ThickPlot   = partial(rnr.contour_plot,key='thickness')
    SpacePlot   = partial(rnr.contour_plot,key='spacing')
    MatPlot     = partial(rnr.contour_plot,key='material')
    TagPlot     = partial(rnr.contour_plot,key='tag')
    IdPlot      = partial(rnr.contour_plot,key='id')

TEXTS = {
'Outline Plot' : RendererS.OutlinePlot, 
'Blocks Plot' : RendererS.BlocksPlot, 
'Pressure Plot' : RendererS.PressPlot, 
'Thickness Plot' : RendererS.ThickPlot, 
'Stiffener Spacing Plot' : RendererS.SpacePlot, 
'Plating Material Plot' : RendererS.MatPlot, 
'Plating Tag Plot' : RendererS.TagPlot, 
'Plating Id Plot' : RendererS.IdPlot 
}
# https://www.pythonguis.com/tutorials/pyside6-plotting-matplotlib/
class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(1, 1, 1)
        super(MplCanvas, self).__init__(self.fig)
    # def change_plot(self, axes):





class GraphicsRenderer(QWidget):
    """
    Class inherited from QWidget to translate the modules.render created 
    matplotlib figures to Widget that can be implemented in the application GUI
    """
    def __init__(self, ship :cls.ship, plot :RendererS, parent: QWidget | None = ..., **kwargs) -> None:
        super().__init__(parent)
        self.fig, self.ax = None, None
        self.ship = ship
        self.call_plot(plot, **kwargs)
    def call_plot(self, plot :RendererS, **kwargs):
        self.fig, self.ax = None, None
        self.fig, self.ax = plot(self.ship, **kwargs)
    def get_fig_ax(self):
        return self.fig, self.ax
        
class DiagramPanel(QWidget):
    '''
    The panel to be imported in the main window that will also handle the
    transition between the different plots 
    '''
    def __init__(self, ship : cls.ship, parent: QWidget | None = ..., **kwargs) -> None:
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




