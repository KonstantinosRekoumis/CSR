"""
Base classes to structure the surrounding code.
As basic classes are chosen the plate class and the
stiffener class. Their fusion gives the stiffened plate class.
"""
import math

import matplotlib.pyplot as plt
import numpy as np

from modules.utilities import normals_2d, linespace, Logger

# Global Parameters
_PLACE_ = {
    "Shell": 0,
    "InnerBottom": 1,
    "Hopper": 2,
    "Wing": 3,
    "Bilge": 4,
    "WeatherDeck": 5,
    "Girder": 6,
    0: "Shell",
    1: "InnerBottom",
    2: "Hopper",
    3: "Wing",
    4: "Bilge",
    5: "WeatherDeck",
    6: "Girder",
}

class Plate:
    """
    The plate class is the bottom plate (no pun intended) class that is responsible for all geometry elements.
    Initializing a plate item requires the start and end point coordinates in meters, the plate's thickness in mm,
    and the plate's chosen material.
    """

    def __init__(
        self, start: tuple, end: tuple, thickness: float, material: str, tag: str
    ):
        try:
            self.tag = _PLACE_[tag]
        except KeyError:
            self.tag = _PLACE_["InnerBottom"]  # Worst Case Scenario
            warn = (
                self.__str__
                + "\nThe plate's original tag is non existent. The existing tags are:"
            )
            Logger.warning(warn)
            [print(_PLACE_[i], ") ->", i) for i in _PLACE_ if type(i) == str]
            Logger.warning("The program defaults to Inner Bottom Plate")
        self.start = start
        self.end = end
        if thickness == 0:
            thickness = 1
        self.thickness = thickness * 1e-3  # convert mm to m
        self.material = material
        self.net_thickness = self.thickness
        # Calculations' Data Output
        self.cor_thickness = -1e-3 if self.tag != 6 else 0
        self.net_thickness_calc = 0
        self.net_thickness_empi = 0
        self.net_thickness_buck = 0
        # Implicitly Calculated Quantities
        self.angle, self.length = self.calc_lna()
        self.area = self.length * self.thickness
        self.Ixx_c, self.Iyy_c = self.calc_I_center(b=self.net_thickness)
        self.CoA = self.calc_CoA()
        self.eta = self.eta_eval()
        # t = net + 50% corrosion Related Calculations and Quantities
        self.n50_thickness = self.net_thickness + 0.5 * self.cor_thickness
        self.n50_area = self.length * self.n50_thickness
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I_center(b=self.n50_thickness)

    def __str__(self):
        if self.tag != 4:
            return f"PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "
        else:
            return f"BILGE PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "

    def calc_lna(self):
        # calculate the plate's angle and length
        dy = self.end[1] - self.start[1]
        dx = self.end[0] - self.start[0]
        try:
            a = math.atan2(dy, dx)
        except ZeroDivisionError:
            if dy > 0:
                a = math.pi / 2
            elif dy <= 0:
                a = -math.pi / 2
        if self.tag != 4:
            l = math.sqrt(dy**2 + dx**2)
        else:
            if abs(dx) == abs(dy):
                l = math.pi * abs(dx) / 2
            else:
                Logger.error(
                    "-- ERROR --\n"
                    + "Edit your design. As the only bilge type supported is quarter circle."
                )
                quit()
        return a, l

    def calc_I_center(self, b):
        """
        Calculate the plate's Moments of Inertia at the center of the plate
        """
        l = self.length
        a = self.angle
        if self.tag != 4:
            Ixx = b * l / 12 * ((b * math.cos(a)) ** 2 + (l * math.sin(a)) ** 2)
            Iyy = b * l / 12 * ((b * math.cos(a + math.pi / 2)) ** 2 
                                + (l * math.sin(a + math.pi / 2)) ** 2
                                )
        else:
            r = l / math.pi * 2
            Ixx = 1 / 16 * math.pi * (r**4 - (r - self.thickness) ** 4)
            Iyy = 1 / 16 * math.pi * (r**4 - (r - self.thickness) ** 4)
            pass
        return Ixx, Iyy

    def calc_CoA(self):
        # calculates Center of Area relative to the Global (0,0)
        if self.tag != 4:
            return (self.start[0] + self.length / 2 * math.cos(self.angle)), (
                self.start[1] + self.length / 2 * math.sin(self.angle)
            )
        else:
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

    def render(self, r_m="w"):
        """
        Rendering utility utilizing the matplotlib framework.
        r_m is the render mode. \'w\' stands for simple line plot
        It also returns a tuple containing significant geometrical properties. (meybe change later)
        """
        X, Y = self.render_data()[:2]
        if r_m == "w":
            plt.plot(X, Y, color="b")
        elif r_m == "wb":
            marker = "."
            if self.tag == 4:
                marker = ""
            plt.plot(X, Y, color="b", marker=marker)
        elif r_m == "wC":
            marker = "."
            if self.tag == 4:
                marker = ""
            plt.plot(X, Y, color="b", marker=marker)
            plt.plot(self.CoA[0], self.CoA[1], color="red", marker="+")

    def render_data(self):
        if self.tag != 4:
            out = [
                (self.start[0], self.end[0]),
                (self.start[1], self.end[1]),
                self.thickness,
                self.material,
                _PLACE_[self.tag],
            ]
        else:
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

            lin = np.linspace(start, end, num=10)
            r = self.end[0] - self.start[0]
            X = startx + np.cos(lin) * abs(r)
            Y = starty + np.sin(lin) * abs(r)
            out = [X, Y, self.thickness, self.material, _PLACE_[self.tag]]

        return out

    def save_data(self):
        return [
            self.start,
            self.end,
            self.thickness * 1e3,
            self.material,
            _PLACE_[self.tag],
        ]

    def calc_I_global(self, Ixx_c, Iyy_c, axis="x"):
        """
        Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'
        (to indicate the Global Axis) or a custom Vertical or Horizontal Axis as a dictionary
        i.e. axis = { 'axis' : 'x', 'offset' : 1.0}
        This indicates a horizontal axis offset to the global axis positive 1 unit.
        """
        if axis == "x":
            # Default Global axis for the prime forces
            Ixx = Ixx_c + self.CoA[1] ** 2 * self.area
            return Ixx
        elif axis == "y":
            Iyy = Iyy_c + self.CoA[0] ** 2 * self.area
            return Iyy
        elif type(axis) is dict:
            try:
                if axis["axis"] == "x":
                    Ixx = Ixx_c + (self.CoA[1] - axis["offset"]) ** 2 * self.area
                    return Ixx
                elif axis["axis"] == "y":
                    Iyy = Iyy_c + (self.CoA[0] - axis["offset"]) ** 2 * self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return 0
            except TypeError:
                print(
                    "The axis dictionary has no proper values.\n",
                    "axis :",
                    axis["axis"],
                    type(axis["axis"]),
                    "\noffset :",
                    axis["offset"],
                    type(axis["offset"]),
                )
                return 0

    def eta_eval(self):
        """
        Evaluates the normal vectors of the plate face. Useful in Pressure offloading
        """
        X, Y = self.render_data()[:2]
        geom = [[X[i], Y[i]] for i in range(len(X))]
        return normals_2d(geom)

    def update(self):
        if self.net_thickness < max(
            self.net_thickness_calc, self.net_thickness_empi, self.net_thickness_buck
        ):
            self.net_thickness = max(
                self.net_thickness_calc,
                self.net_thickness_empi,
                self.net_thickness_buck,
            )
        self.thickness = self.net_thickness + self.cor_thickness
        # They are not supposed to change for the time being
        self.area = self.length * self.thickness
        self.Ixx_c, self.Iyy_c = self.calc_I_center(b=self.net_thickness)
        self.CoA = self.calc_CoA()
        self.eta = self.eta_eval()
        self.n50_thickness = self.net_thickness + 0.5 * self.cor_thickness
        self.n50_area = self.length * self.n50_thickness
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I_center(b=self.n50_thickness)

    def debug(self):
        print("start : ", self.start)
        print("end : ", self.end)
        print("thickness : ", self.thickness)
        print("net_thickness : ", self.net_thickness)
        print("cor_thickness : ", self.cor_thickness)
        print("material : ", self.material)

        print("self.angle : ", self.angle)
        print("self.length : ", self.length)
        print("self.area : ", self.area)
        print("self.Ixx_c : ", self.Ixx_c)
        print("self.Iyy_c : ", self.Iyy_c)
        print("self.CoA : ", self.CoA)
        print("self.eta : ", self.eta)
        print("self.n50_thickness : ", self.n50_thickness)
        print("self.n50_area : ", self.n50_area)
        print("self.n50_Ixx_c : ", self.n50_Ixx_c)


class Stiffener:
    """
    The stiffener class is a class derived from the plate class. Stiffener is consisted of or more plates.
    To create a stiffener insert its form as \'fb\' -> Flat Bars, \'g\' -> for angular beams, \'t\' for t beams and \'bb\' for bulbous bars.
    Dimensions are entered as a dictionary of keys \'lx\', \'bx\' x referring to web and\or flange length and thickness respectively.
    Material is to be inserted like in the plate class, while only the root coordinates are required.
    Angle is used to make the stiffener perpendicular relative to the supported plate's angle.
    """

    def __init__(
        self,
        form: str,
        dimensions: dict,
        angle: float,
        root: tuple[float],
        material: str,
        tag: str,
    ):
        # Support for only flat bars, T bars and angled bars
        # dimensions lw -> length, bw -> thickness
        self.type = form
        self.material = material
        self.Ixx_c = 0
        self.Iyy_c = 0
        self.area = 0
        # n50
        self.n50_area = 0
        self.n50_Ixx_c = 0
        self.n50_Iyy_c = 0
        self.Z_rule = 0
        self.dimensions = dimensions
        if self.type == "fb":  # flat bar
            pw = Plate(
                root,
                (
                    root[0] + math.cos(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
                    root[1] + math.sin(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
                ),
                dimensions["bw"],
                material,
                tag,
            )
            self.plates = [pw]
        elif self.type == "g":  # angled bar
            end_web = (
                root[0] + math.cos(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
                root[1] + math.sin(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
            )
            pw = Plate(root, end_web, dimensions["bw"], material, tag)
            end_flange = (
                end_web[0] + math.cos(angle) * dimensions["lf"] * 1e-3,
                end_web[1] + math.sin(angle) * dimensions["lf"] * 1e-3,
            )
            pf = Plate(end_web, end_flange, dimensions["bf"], material, tag)
            self.plates = [pw, pf]
        elif self.type == "tb":  # T bar
            end_web = (
                root[0] + math.cos(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
                root[1] + math.sin(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
            )
            pw = Plate(root, end_web, dimensions["bw"], material, tag)
            start_flange = (
                end_web[0] - math.cos(angle) * dimensions["lf"] / 2 * 1e-3,
                end_web[1] - math.sin(angle) * dimensions["lf"] / 2 * 1e-3,
            )
            end_flange = (
                end_web[0] + math.cos(angle) * dimensions["lf"] / 2 * 1e-3,
                end_web[1] + math.sin(angle) * dimensions["lf"] / 2 * 1e-3,
            )
            pf = Plate(start_flange, end_flange, dimensions["bf"], material, tag)
            self.plates = [pw, pf]

        self.calc_CoA()
        self.calc_I()

    def __repr__(self) -> str:
        dim = "{"
        for i, plate in enumerate(self.plates):
            if i == 0:
                dim += f"'lw':{plate.length * 1e3},'bw':{plate.thickness * 1e3}"
            else:
                dim += f",'l{i}':{plate.length * 1e3},'b{i}':{plate.thickness * 1e3}"

        return f"stiffener(type: {self.type},dimensions : {dim}" + "}"

    def calc_CoA(self):
        area = 0
        n50_area = 0
        MoM_x = 0
        MoM_y = 0
        for i in self.plates:
            area += i.area
            n50_area += i.n50_area
            MoM_x += i.area * i.CoA[1]
            MoM_y += i.area * i.CoA[0]
        self.CoA = (MoM_y / area, MoM_x / area)
        self.area = area
        self.n50_area = n50_area

    def calc_I(self):
        Ixx = 0
        Iyy = 0
        n50_Ixx = 0
        n50_Iyy = 0

        for i in self.plates:
            Ixx += i.calc_I_global(
                i.Ixx_c, i.Iyy_c, {"axis": "x", "offset": self.CoA[1]}
            )
            n50_Ixx += i.calc_I_global(
                i.n50_Ixx_c, i.n50_Iyy_c, {"axis": "x", "offset": self.CoA[1]}
            )
            Iyy += i.calc_I_global(
                i.Ixx_c, i.Iyy_c, {"axis": "y", "offset": self.CoA[0]}
            )
            n50_Iyy += i.calc_I_global(
                i.n50_Ixx_c, i.n50_Iyy_c, {"axis": "y", "offset": self.CoA[0]}
            )

        self.Ixx_c = Ixx
        self.Iyy_c = Iyy
        self.n50_Ixx_c = n50_Ixx
        self.n50_Iyy_c = n50_Iyy

    def calc_I_global(self, Ixx_c, Iyy_c, axis="x"):
        """Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
        or an custom Vertical or Horizontal Axis as a dictionary
        ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)
        """
        if axis == "x":
            # Default Global axis for the prime forces
            Ixx = Ixx_c + self.CoA[1] ** 2 * self.area
            return Ixx
        elif axis == "y":
            Iyy = Iyy_c + self.CoA[0] ** 2 * self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis["axis"] == "x":
                    Ixx = Ixx_c + (self.CoA[1] - axis["offset"]) ** 2 * self.area
                    return Ixx
                elif axis["axis"] == "y":
                    Iyy = Iyy_c + (self.CoA[0] - axis["offset"]) ** 2 * self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print(
                    "The axis dictionary has no proper values.\n",
                    "axis :",
                    axis["axis"],
                    type(axis["axis"]),
                    "\noffset :",
                    axis["offset"],
                    type(axis["offset"]),
                )
                return None

    def calc_Z(self):
        if self.type in ("tb", "g"):
            """
                ----x----               ----x----
                    |                   |
                    |                   |
                    x o       OR        x   o
                    |                   |
            ________|________   ________|________
            """
            ylc_web = self.plates[0].length / 2
            ylc_flg = self.plates[0].length

            ylc_st = (ylc_flg * self.plates[1].area + ylc_web * self.plates[0].area) / (
                self.area
            )

            Ixx = (
                self.plates[0].net_thickness * self.plates[0].length ** 3 / 12
                + self.plates[1].net_thickness ** 3 * self.plates[1].length / 12
                + self.plates[0].area * (ylc_web - ylc_st) ** 2  # Parallel Axis Theorem
                + self.plates[1].area * (ylc_flg - ylc_st) ** 2  # Parallel Axis Theorem
            )
            return Ixx / (ylc_flg - ylc_st)
        elif self.type in ("fb"):
            Ixx = self.plates[0].net_thickness * self.plates[0].length ** 3 / 12
        return Ixx / (self.plates[0].length / 2)

    def render(self, r_m="w"):
        for i in self.plates:
            i.render()

    def render_data(self):
        X = []
        Y = []
        T = []
        M = []
        for i in self.plates:
            tmp = i.render_data()
            [X.append(i) for i in tmp[0]]
            [Y.append(i) for i in tmp[1]]
            T.append(tmp[2])
            M.append(tmp[3])
        return X, Y, T, M

    def update(self):
        for plate in self.plates:
            plate.update()
        self.calc_CoA()
        self.calc_I()


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
