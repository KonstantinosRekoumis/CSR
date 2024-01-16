from modules.baseclass.block import Block, SpaceType
from modules.baseclass.stiff_plate import StiffPlate
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger


@auto_str
class SeaSur(Block):
    def __init__(self, list_plates_id: list[int]):
        super().__init__("SEA", True, SpaceType.Sea , list_plates_id)

    def get_coords(self, stiff_plates: list[StiffPlate]):
        super().get_coords(stiff_plates)
        # add a buffer zone for sea of 2 m
        if len(self.coords) == 0:
            Logger.error("SEA Boundary plates are missing!. The program terminates...")
        end = self.coords[-1]
        self.coords.append((end[0] + 2, end[1]))
        self.coords.append((end[0] + 2, self.coords[0][1] - 2))
        self.coords.append((self.coords[0][0], self.coords[0][1] - 2))
