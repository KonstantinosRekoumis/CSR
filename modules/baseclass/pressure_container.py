import numpy as np
from modules.baseclass.plating.stiff_plate import StiffPlate
from baseclass.block import Block
from physics.data import _check_cond

class PressureContainer:
    def __init__(self, plate: StiffPlate, block: Block) -> None:
        """_summary_

        Args:
            plate (StiffPlate): The stiff plate whose pressure distributions are stored
            block (Block): The Block containing the Pressure Container
        """        
        self.plate = plate
        self.block = block
        self.pressure_grid = self.plate.pressure_grid
        self.evaluator = None
        self._pressure_distro = []

    @property
    def pressure_distro(self):
        return self._pressure_distro
    
    @pressure_distro.setter
    def pressure_distro(self):
        self._pressure_distro = self.evaluator(self.pressure_grid)

class BSP01_PressureContainer(PressureContainer):
    def __init__(self, plate: StiffPlate, block: Block) -> None:
        super().__init__(plate, block)

