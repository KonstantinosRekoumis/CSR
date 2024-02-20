from utils.logger import Logger
from baseclass.plating.plate import Plate, _PLACE_

class SplinePlate(Plate):
    """This type of plate is to be used to model complex plate geometry.
    There is no need to create something more complicated than that. 

    We can modify the SplinePlate to use it with different types to describe a
    spline (list of points, factors of a polynomial curve, a curve object, etc.)

    Args:
        Plate (_type_): _description_
    """
    def __init__(self, data_coords: list[tuple], thickness: float, material: str, tag: str):
        raise NotImplementedError
        try:
            self.tag = _PLACE_[tag]
        except KeyError:
            self.tag = _PLACE_["InnerBottom"]  # Worst Case Scenario
            warn = (
                    self.__str__
                    + "\nThe plate's original tag is non existent. The existing tags are:"
            )
            Logger.warning(warn)
            [print(_PLACE_[i], ") ->", i) for i in _PLACE_ if isinstance(i, str)]
            Logger.warning("The program defaults to Inner Bottom Plate")
        self.start = data_coords[0]
        self.end = data_coords[-1]
        self.data_coords = data_coords
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