import math

import numpy as np
from matplotlib import pyplot as plt

from modules.utils.decorators import auto_str
from modules.utils.logger import Logger
from modules.utils.operations import normals_2d

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
@auto_str
class Bilge(Plate):
    def __str__(self):
        return f"BILGE PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "
@auto_str
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
        self.Ixx_c, self.Iyy_c = self.calc_I_center(self.net_thickness)
        self.CoA = self.calc_CoA()
        self.eta = self.eta_eval()
        # t = net + 50% corrosion Related Calculations and Quantities
        self.n50_thickness = self.net_thickness + 0.5 * self.cor_thickness
        self.n50_area = self.length * self.n50_thickness
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I_center(b=self.n50_thickness)

    def __str__(self):
        return f"PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "
            
    def calc_length(self, dx, dy):
        raise NotImplementedError
    
    def calc_angle(self, dx, dy):
        try:
            return math.atan2(dy, dx)
        except ZeroDivisionError:
            if dy > 0:
                return math.pi / 2
            elif dy <= 0:
                return -math.pi / 2

    def calc_lna(self):
        # calculate the plate's angle and length
        dy = self.end[1] - self.start[1]
        dx = self.end[0] - self.start[0]
        return self.calc_angle(dx, dy), self.calc_length(dx, dy)

    def calc_I_center(self, b: float):
        """
        Calculate the plate's Moments of Inertia at the center of the plate

        Args:
            b (float) : The desired thickness to perform calculations with
        """
        raise NotImplementedError
        
        

    def calc_CoA(self):
        # calculates Center of Area relative to the Global (0,0)
        raise NotImplementedError

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
        elif isinstance(axis, dict):
            try:
                if axis["axis"] == "x":
                    Ixx = Ixx_c + (self.CoA[1] - axis["offset"]) ** 2 * self.area
                    return Ixx
                elif axis["axis"] == "y":
                    Iyy = Iyy_c + (self.CoA[0] - axis["offset"]) ** 2 * self.area
                    return Iyy
            except KeyError | TypeError as e:
                if isinstance(e, KeyError):
                    Logger.error("The axis dictionary is not properly structured", rethrow=e)
        Logger.error(f"Improper axis values {axis}", rethrow=e)

    def eta_eval(self):
        """
        Evaluates the normal vectors of the plate face. Useful in Pressure offloading
        """
        x, y = self.render_data()[:2]
        geom = [[x[i], y[i]] for i in range(len(x))]
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
