import math

from matplotlib import pyplot as plt

from modules.baseclass.plating.plate import Plate
from modules.baseclass.plating.linear_plate import LinearPlate
from modules.baseclass.plating.quart_circ_plate import QuartCircPlate
from modules.baseclass.plating.spline_plate import SplinePlate
from modules.baseclass.plating.stiffener import Stiffener
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger
from modules.utils.operations import linespace
@auto_str
class StiffGroup:

    def __init__(self, plate: Plate, spacing: float, start_pad: float, stiffener_type: dict, end_pad: float, N: int | None = None):
        """Stiffeners are grouped together to enable the user to model more complex stiffening configurations and not be limited 
        in a single stiffener type per stiffened plate.

        Note that either an end padding can be provided or a Number of Stiffeners to be input. As the target is to have a constant spacing
        that is input by the user, the user can either provide a the distance from the end and let the class calculate the number of stiffeners
        or explicitly provide the number of stiffeners and ignore the end padding.

        Args:
            plate (Plate):  The base plate to take the root of the geometry
            spacing [mm] (float):  The spacing between each stiffener
            start_pad [mm] (float): The offset from the start of the plate to the start of the group
            stiffener_type (dict): A dictionary containing the geometric properties of the stiffener
            end_pad [mm] (float): The offset from the end of the plate to the end of the group.
        Kwargs:
            N (int, optional): The number of stiffeners in the group. Defaults to 1.
        """
        self.base_plate = plate
        self.spacing = spacing * 1e-3
        self.start_pad = start_pad * 1e-3
        self.end_pad = end_pad * 1e-3
        self.N = N
        if spacing == 0 : Logger.error(f"The spacing you provided is 0. StiffGroup = {self}")

        self.stiffeners: list[Stiffener] = []

        if self.N is None:
            net_l = self.base_plate.length - self.start_pad - self.end_pad
            self.N = math.floor(net_l / self.spacing)
        else:
            if (end_pad:=(self.base_plate.length - self.start_pad - self.N * self.spacing)) <= 0:
                Logger.error(f"Stiff Group has more elements than the plate can support!")                 
            self.end_pad = end_pad
        _range = linespace(1, self.N, 1, truncate_end=False)
        for i in _range:
            root = (
                self.base_plate.start[0]
                + math.cos(self.base_plate.angle) * (self.spacing * i + self.start_pad),
                self.base_plate.start[1]
                + math.sin(self.base_plate.angle) * (self.spacing * i + self.start_pad),
            )
            self.stiffeners.append(
                Stiffener(
                    stiffener_type["type"],
                    stiffener_type["dimensions"],
                    self.base_plate.angle,
                    root,
                    stiffener_type["material"],
                    plate.tag,
                )
            )
        self.calc_center_of_area()
        self.calc_inertia()

    def calc_center_of_area(self):
        total_A = 0
        total_A_n50 = 0
        total_Mx = 0
        total_My = 0
        for i in self.stiffeners:
            total_A += i.area
            total_A_n50 += i.n50_area
            total_Mx += i.area * i.CoA[1]
            total_My += i.area * i.CoA[0]
        self.CoA = (total_My / total_A, total_Mx / total_A)
        self.area = total_A
        self.n50_area = total_A_n50
    
    def calc_inertia(self):
        Iyy, Ixx = 0, 0
        for i in self.stiffeners:
            Ixx += i.calc_I_global(
                    i.Ixx_c, i.Iyy_c, {"axis": "x", "offset": self.CoA[1]}
                )
            Iyy += i.calc_I_global(
                i.Ixx_c, i.Iyy_c, {"axis": "y", "offset": self.CoA[0]}
            )
        self.Ixx = Ixx
        self.Iyy = Iyy
    
    def update(self):
        for stiff in self.stiffeners:
            stiff.update()
        self.calc_center_of_area()
        self.calc_inertia()

    def save_data(self) -> str:
        return {["stiffener_type"]: self.stiffeners[0].save_data(),
                ["spacing"]: round(self.spacing*1e3, 2),
                ["start_pad"]: round(self.start_pad*1e3, 2),
                ["end_pad"]: round(self.end_pad*1e3, 2),
                ["N"]: self.N}
            
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
    psm_spacing is in m.
    """

    def __init__(
            self,
            id: int,
            plate: Plate,
            stiffeners: list[StiffGroup],
            psm_spacing: float,
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
            psm_spacing (float): Primary Structural Members spacing in meters
            null (bool, optional): Keyword argument to disregard the plate for
            any strength calculations. Defaults to False.
        """
        self.id = id
        self.plate = plate
        self.tag = plate.tag  # it doesn't make sense not to grab it here
        self.stiffener_groups = []
        self.stiffeners = [] # simplify stiffener data acquisition
        self.null = null
        self.psm_spacing = psm_spacing
        self.b_eff = 0
        # if self.plate.tag != 4 or not self.null and len(stiffener_) != 0:
        if isinstance(self.plate, LinearPlate) and not self.null:
            self.stiffener_groups = stiffeners
            if len(self.stiffener_groups) == 0:
                self.spacing = self.plate.length
                self.s_pad = 0
                self.e_pad = 0
            else:
                spacing = []
                s_pad = []
                e_pad = []
                for group in stiffeners:
                    spacing.append(group.spacing)
                    s_pad.append(group.start_pad)
                    e_pad.append(group.end_pad)

                self.spacing = sum(spacing) / len(spacing)
                self.s_pad = min(s_pad)
                self.e_pad = min(e_pad)
                
        for group in self.stiffener_groups:
            for stiffener in group.stiffeners:
                self.stiffeners.append(stiffener)
            
        self.CoA = []
        self.area = 0
        self.n50_area = 0
        self.center_of_area()
        self.Ixx_c, self.Iyy_c = self.calc_I(n50=False)
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I(n50=True)
        self.Pressure = {}
        # renew stiffener

    def L_eff(self):
        if len(self.stiffener_groups) != 0 and self.tag != 6:
            bef = min(self.spacing, self.psm_spacing * 0.2)
            if self.plate.net_thickness < 8 * 1e-3:
                bef = min(0.6, bef)
            self.plate.length = len(self.stiffener_groups) * bef
            self.update()
            self.b_eff = bef

    def __str__(self) -> str:
        tmp = str(self.stiffener_groups[0]) if len(self.stiffener_groups) != 0 else "No Stiffeners"
        return f"stiff_plate({self.id},{self.plate},{self.spacing},{tmp})"

    def center_of_area(self):
        total_A = self.plate.area
        total_A_n50 = self.plate.n50_area
        total_Mx = self.plate.area * self.plate.CoA[1]
        total_My = self.plate.area * self.plate.CoA[0]
        if len(self.stiffener_groups) != 0:
            for i in self.stiffener_groups:
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
            if len(self.stiffener_groups) != 0:
                for i in self.stiffener_groups:
                    Ixx += i.Ixx
                    Iyy += i.Iyy
            return Ixx, Iyy

        Ixx = self.plate.calc_I_global(
            self.plate.Ixx_c, self.plate.Iyy_c, {"axis": "x", "offset": self.CoA[1]}
        )
        Iyy = self.plate.calc_I_global(
            self.plate.Ixx_c, self.plate.Iyy_c, {"axis": "y", "offset": self.CoA[0]}
        )
        if len(self.stiffener_groups) != 0:
            for i in self.stiffener_groups:
                Ixx += i.Ixx
                Iyy += i.Iyy

        return Ixx, Iyy

    def render(self, r_m="w_b"):
        plt.axis("square")
        self.plate.render(r_m=r_m)
        [i.render() for i in self.stiffener_groups]

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
        for stiff in self.stiffener_groups:
            stiff.update()
        self.center_of_area()
        self.Ixx, self.Iyy = self.calc_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.calc_I(n50=True)

    def save_data(self):
        return {
            "id": self.id,
            "plate": self.plate.save_data(),
            "stiffeners": [group.save_data() for group in self.stiffener_groups],
            "psm_spacing": self.psm_spacing,
            "null": self.null,
        }