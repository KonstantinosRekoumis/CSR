import math
from utils.logger import Logger
from baseclass.plating.plate import Plate
from modules.utils.decorators import auto_str

@auto_str
class QuartCircPlate(Plate):
    def __init__(self, start: tuple, end: tuple, thickness: float, material: str, tag: str):
        super().__init__(start, end, thickness, material, tag)
    
    def calc_length(self, dx, dy):
        if abs(dx) == abs(dy):
            return math.pi * abs(dx) / 2
        Logger.error("Edit your design. You specified a quarter circle plate whose dx ({dx}) =/= dy ({dy}).")
    
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