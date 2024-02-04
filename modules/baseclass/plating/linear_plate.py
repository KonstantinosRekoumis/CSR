import math
from baseclass.plating.plate import Plate
from modules.utils.decorators import auto_str

@auto_str
class LinearPlate(Plate):
    def __init__(self, start: tuple, end: tuple, thickness: float, material: str, tag: str):
        super().__init__(start, end, thickness, material, tag)
    def calc_length(self, dx, dy):
        return math.sqrt(dy ** 2 + dx ** 2)
    def calc_I_center(self, b):
        l = self.length
        a = self.angle
        Ixx = b * l / 12 * ((b * math.cos(a)) ** 2 + (l * math.sin(a)) ** 2)
        Iyy = b * l / 12 * ((b * math.cos(a + math.pi / 2)) ** 2
                            + (l * math.sin(a + math.pi / 2)) ** 2
                            )
        return Ixx, Iyy
    def calc_CoA(self):
        return (self.start[0] + self.length / 2 * math.cos(self.angle)), (
                    self.start[1] + self.length / 2 * math.sin(self.angle)
            )