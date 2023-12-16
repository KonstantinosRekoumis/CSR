import math

from matplotlib import pyplot as plt

from modules.baseclass.plate import Plate
from modules.baseclass.stiffener import Stiffener
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger
from modules.utils.operations import linespace


@auto_str
class StiffPlate:
    """
    The stiff_plate class is the Union of the plate and the stiffener(s).
    Its args are :
    plate -> A plate object
    spacing -> A float number, to express the distance between two stiffeners in mm.
    s_pad, e_pad -> Float numbers, to express the padding distance (in mm) of the stiffeners with
    respect to the starting and ending edge of the base plate.
    stiffener_dict -> A dict containing data to create stiffeners : {type : str, dims : [float (in mm)],mat:str}
    PSM_spacing is in m.
    """

    def __init__(
            self,
            id: int,
            plate: Plate,
            spacing: float,
            s_pad: float,
            e_pad: float,
            stiffener_: dict,
            skip: int,
            PSM_spacing: float,
            null: bool = False,
    ):
        """`StiffPlate` class

        Args:
            id (int): The plate's assigned id
            plate (Plate): A plate object, the basis of the StiffPlate's geometry
            spacing (float): A float number, to express the distance between two stiffeners in mm.
            s_pad (float): The padding of the stiffeners from the start of the plate
            e_pad (float): The padding of the stiffeners from the end of the plate
            stiffener_ (dict): A dict containing data to create stiffeners : `{type : str, dims : [float (in mm)],mat:str}`
            skip (int): Consider $skip = N$, the Nth stiffener is ignored and
            not created
            PSM_spacing (float): Primary Structural Members spacing in meters
            null (bool, optional): Keyword argument to disregard the plate for
            any strength calculations. Defaults to False.
        """
        self.id = id
        self.plate = plate
        self.tag = plate.tag  # it doesn't make sense not to grab it here
        self.stiffeners = []
        self.spacing = spacing * 1e-3
        self.s_pad = s_pad * 1e-3
        self.e_pad = e_pad * 1e-3
        self.skip = skip
        self.null = null
        self.PSM_spacing = PSM_spacing
        self.b_eff = 0
        # if self.plate.tag != 4 or not self.null and len(stiffener_) != 0:
        if self.tag != 4 and not self.null and len(stiffener_) != 0:
            try:
                net_l = self.plate.length - self.s_pad - self.e_pad
                N = math.floor(net_l / self.spacing)
                _range = linespace(1, N, 1, skip=skip, truncate_end=False)
            except ZeroDivisionError:
                Logger.error(
                    f"(classes.py) stiff_plate: Plate {self} has no valid dimensions."
                )
                quit()
            for i in _range:
                root = (
                    self.plate.start[0]
                    + math.cos(self.plate.angle) * (self.spacing * i + self.s_pad),
                    self.plate.start[1]
                    + math.sin(self.plate.angle) * (self.spacing * i + self.s_pad),
                )
                self.stiffeners.append(
                    Stiffener(
                        stiffener_["type"],
                        stiffener_["dimensions"],
                        self.plate.angle,
                        root,
                        stiffener_["material"],
                        plate.tag,
                    )
                )
        self.CoA = []
        self.area = 0
        self.n50_area = 0
        self.center_of_area()
        self.Ixx_c, self.Iyy_c = self.calc_I(n50=False)
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I(n50=True)
        self.Pressure = {}
        # renew stiffener

    def L_eff(self):
        if len(self.stiffeners) != 0 and self.tag != 6:
            bef = min(self.spacing, self.PSM_spacing * 0.2)
            if self.plate.net_thickness < 8 * 1e-3:
                bef = min(0.6, bef)
            self.plate.length = len(self.stiffeners) * bef
            self.update()
            self.b_eff = bef

    def __repr__(self) -> str:
        tmp = repr(self.stiffeners[0]) if len(self.stiffeners) != 0 else "No Stiffeners"
        return f"stiff_plate({self.id},{self.plate},{self.spacing},{tmp})"

    def center_of_area(self):
        total_A = self.plate.area
        total_A_n50 = self.plate.n50_area
        total_Mx = self.plate.area * self.plate.CoA[1]
        total_My = self.plate.area * self.plate.CoA[0]
        if len(self.stiffeners) != 0:
            for i in self.stiffeners:
                total_A += i.area
                total_A_n50 += i.n50_area
                total_Mx += i.area * i.CoA[1]
                total_My += i.area * i.CoA[0]

        self.CoA = (total_My / total_A, total_Mx / total_A)
        self.area = total_A
        self.n50_area = total_A_n50

    def calc_I(self, n50):
        if n50:
            Ixx = self.plate.calc_I_global(
                self.plate.n50_Ixx_c,
                self.plate.n50_Iyy_c,
                {"axis": "x", "offset": self.CoA[1]},
            )
            Iyy = self.plate.calc_I_global(
                self.plate.n50_Ixx_c,
                self.plate.n50_Iyy_c,
                {"axis": "y", "offset": self.CoA[0]},
            )
            if len(self.stiffeners) != 0:
                for i in self.stiffeners:
                    Ixx += i.calc_I_global(
                        i.n50_Ixx_c, i.n50_Iyy_c, {"axis": "x", "offset": self.CoA[1]}
                    )
                    Iyy += i.calc_I_global(
                        i.n50_Ixx_c, i.n50_Iyy_c, {"axis": "y", "offset": self.CoA[0]}
                    )
            return Ixx, Iyy

        Ixx = self.plate.calc_I_global(
            self.plate.Ixx_c, self.plate.Iyy_c, {"axis": "x", "offset": self.CoA[1]}
        )
        Iyy = self.plate.calc_I_global(
            self.plate.Ixx_c, self.plate.Iyy_c, {"axis": "y", "offset": self.CoA[0]}
        )
        if len(self.stiffeners) != 0:
            for i in self.stiffeners:
                Ixx += i.calc_I_global(
                    i.Ixx_c, i.Iyy_c, {"axis": "x", "offset": self.CoA[1]}
                )
                Iyy += i.calc_I_global(
                    i.Ixx_c, i.Iyy_c, {"axis": "y", "offset": self.CoA[0]}
                )
        return Ixx, Iyy

    def render(self, r_m="w_b"):
        plt.axis("square")
        self.plate.render(r_m=r_m)
        [i.render() for i in self.stiffeners]

    def local_P(self, key, point):
        """
        !!! USE ONLY WITH CUSTOM TRY - EXCEPT TO CATCH SPECIAL CASES !!!
        ! point can be whatever. As i have no brain capacity to code a check,
        PLZ use only the roots of the stiffeners
        """
        if self.tag == 6:
            Logger.error(
                "(classes.py) stiff_plate/local_P: Pressures are not currently calculated for girders and bulkheads..."
            )
            quit()
        min_r = 1e5
        index = 0
        for i, data in enumerate(self.Pressure[key]):
            radius = math.sqrt((data[0] - point[0]) ** 2 + (data[1] - point[1]) ** 2)
            if min_r > radius:
                index = i
                min_r = radius
        return self.Pressure[key][index][-1]

    def update(self):
        self.plate.update()
        for stiff in self.stiffeners:
            stiff.update()
        self.center_of_area()
        self.Ixx, self.Iyy = self.calc_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.calc_I(n50=True)
