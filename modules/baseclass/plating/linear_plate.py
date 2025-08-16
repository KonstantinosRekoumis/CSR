import math

import numpy as np
from modules.baseclass.plating.plate import _PLACE_, Plate
from modules.utils.decorators import auto_str


@auto_str
class LinearPlate(Plate, prefix="LINEAR"):
    def calc_length(self, dx:float, dy:float) -> float:
        return math.sqrt(dy**2 + dx**2)

    def calc_I_center(self, b:float) -> tuple[float, float]:  # noqa: N802
        l = self.length  # noqa: E741
        a = self.angle
        ixx = b * l / 12 * ((b * math.cos(a)) ** 2 + (l * math.sin(a)) ** 2)
        iyy = ( b * l / 12 * (
                (b * math.cos(a + math.pi / 2)) ** 2
                + (l * math.sin(a + math.pi / 2)) ** 2))
        return ixx, iyy

    def calc_CoA(self) -> tuple[float, float]:  # noqa: N802
        return (self.start[0] + self.length / 2 * math.cos(self.angle)), (
            self.start[1] + self.length / 2 * math.sin(self.angle)
        )

    def calculate_grid(self, res: int = 10) -> list[list[float]]:
        lin_ = np.linspace(0, self.length, res, endpoint=True)
        x = self.start[0] + lin_ * np.cos(self.angle)
        y = self.start[1] + lin_ * np.cos(self.angle)
        # return np.transpose(np.array((x,y)))
        return [[x[i], y[i]] for i in range(len(x))]

    def render_data(self) :  # noqa: ANN201
        return (
            (self.start[0], self.end[0]),
            (self.start[1], self.end[1]),
            self.thickness,
            self.material,
            _PLACE_[self.tag],
        )

    def save_data(self) -> tuple[tuple, tuple, float, str, str, str]:
        out = super().save_data()
        out["prefix"] = "LINEAR"
        return out
