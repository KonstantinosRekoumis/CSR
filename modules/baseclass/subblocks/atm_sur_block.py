from modules.baseclass.block import Block
from modules.baseclass.stiff_plate import StiffPlate
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger


@auto_str
class AtmSur(Block):
    def __init__(self, list_plates_id: list[int]):
        super().__init__("ATM", True, 'VOID', list_plates_id)
        self.space_type = "ATM"

    def get_coords(self, stiff_plates: list[StiffPlate]):
        super().get_coords(stiff_plates)
        # add a buffer zone for atmosphere of 2 m
        if len(self.coords) == 0:
            Logger.error("WEATHER DECK Boundary plates are missing!. The program terminates...")
            quit()
        end = self.coords[-1]
        self.coords.append((end[0], end[1] + 2))
        self.coords.append((self.coords[0][0] + 2, self.coords[0][1] + 2))
        self.coords.append((self.coords[0][0] + 2, self.coords[0][1]))
