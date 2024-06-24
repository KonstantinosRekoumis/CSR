import math

import numpy as np
from modules.utils.logger import Logger
from modules.baseclass.plating.plate import Plate, _PLACE_
from modules.utils.decorators import auto_str

@auto_str
class QuartCircPlate(Plate, prefix="QUART_C"):
    """QuartCirclePlate class is introduced to model the plates that have a 
    circular geometry. It is an extension of the Plate base class that handles 
    said quarter of circle geometry commonly found in the Bilge Plates.

    By explicitly modelling a quarter circle plate, we keep the project more simple 
    for the time being as it would be too time consuming to model a more complex 
    abstraction for non-linear geometries (See SplinePlate class).

    Inherits:
        Plate : The base class for all the plate Child Classes
    """

    def calc_length(self, dx, dy):
        if abs(dx) == abs(dy):
            return math.pi * abs(dx) / 2
        Logger.error(f"Edit your design. You specified a quarter circle plate whose dx ({dx}) =/= dy ({dy}).")
    
    def calc_I_center(self, b: float):
        r = self.length / math.pi * 2
        Ixx = 1 / 16 * math.pi * (r ** 4 - (r - self.thickness) ** 4)
        Iyy = 1 / 16 * math.pi * (r ** 4 - (r - self.thickness) ** 4)
        return Ixx, Iyy
    
    def calc_CoA(self):
        r = self.length / math.pi * 2
        if 0 < self.angle < math.pi / 2:  # 1st quarter
            startx = self.start[0]
            starty = self.end[1]
            return startx + (2 * r / math.pi), starty - (2 * r / math.pi)
        elif 0 < self.angle < math.pi:  # 2nd quarter
            startx = self.end[0]
            starty = self.start[1]
            return startx + (2 * r / math.pi), starty + (2 * r / math.pi)
        elif 0 > self.angle > -math.pi / 2:
            startx = self.end[0]
            starty = self.start[1]
            return startx - (2 * r / math.pi), starty - (2 * r / math.pi)
        elif 0 > self.angle > -math.pi:
            startx = self.start[0]
            starty = self.end[1]
            return startx - (2 * r / math.pi), starty + (2 * r / math.pi)
        
    def calculate_grid(self,  res = 10):
        if 0 < self.angle < math.pi / 2:
            start = -math.pi / 2
            end = 0
            startx = self.start[0]
            starty = self.end[1]
        elif 0 < self.angle < math.pi:
            start = 0
            end = math.pi / 2
            startx = self.end[0]
            starty = self.start[1]
        elif 0 > self.angle > -math.pi / 2:
            start = -math.pi
            end = -math.pi / 2
            startx = self.end[0]
            starty = self.start[1]
        elif 0 > self.angle > -math.pi:
            start = math.pi / 2
            end = math.pi
            startx = self.start[0]
            starty = self.end[1]

        lin = np.linspace(start, end, num=res)
        r = self.end[0] - self.start[0]
        X = startx + np.cos(lin) * abs(r)
        Y = starty + np.sin(lin) * abs(r)
        return X, Y
        
    def render_data(self) -> tuple[tuple, tuple, float, str, str]:
        return *self.calculate_grid(), self.thickness, self.material, _PLACE_[self.tag]
    
    def save_data(self) -> tuple[tuple, tuple, float, str, str, str]:
        out =  super().save_data()
        out["prefix"] = "QUART_C"
        return out