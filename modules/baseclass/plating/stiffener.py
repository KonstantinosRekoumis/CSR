import math

# from modules.baseclass.plating.plate import Plate
from modules.baseclass.plating.linear_plate import LinearPlate
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger


@auto_str
class Stiffener:
    """
    The stiffener class is a class derived from the plate class. Stiffener is consisted of or more plates.
    To create a stiffener insert its form as:

     -  `\'fb\'` -> Flat Bars
     - `\'g\'` -> for angular beams
     - `\'t\'` for t beams 
     - `\'bb\'` for bulbous bars.
    
    Dimensions are entered as a dictionary of keys \'lx\', \'bx\' x referring to web and/or flange length and thickness respectively.
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
            pw = LinearPlate(
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
            pw = LinearPlate(root, end_web, dimensions["bw"], material, tag)
            end_flange = (
                end_web[0] + math.cos(angle) * dimensions["lf"] * 1e-3,
                end_web[1] + math.sin(angle) * dimensions["lf"] * 1e-3,
            )
            pf = LinearPlate(end_web, end_flange, dimensions["bf"], material, tag)
            self.plates = [pw, pf]
        elif self.type == "tb":  # T bar
            end_web = (
                root[0] + math.cos(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
                root[1] + math.sin(angle + math.pi / 2) * dimensions["lw"] * 1e-3,
            )
            pw = LinearPlate(root, end_web, dimensions["bw"], material, tag)
            start_flange = (
                end_web[0] - math.cos(angle) * dimensions["lf"] / 2 * 1e-3,
                end_web[1] - math.sin(angle) * dimensions["lf"] / 2 * 1e-3,
            )
            end_flange = (
                end_web[0] + math.cos(angle) * dimensions["lf"] / 2 * 1e-3,
                end_web[1] + math.sin(angle) * dimensions["lf"] / 2 * 1e-3,
            )
            pf = LinearPlate(start_flange, end_flange, dimensions["bf"], material, tag)
            self.plates = [pw, pf]

        self.calc_CoA()
        self.calc_I()

    def __str__(self) -> str:
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

    def save_data(self):
        # Save data to JSON format
        tags = {0: 'lw' , 1: 'bw' , 2: 'lf' , 3: 'bf' }
        dim = []
        for i in self.plates:
            dim.append(i.length * 1e3)
            dim.append(i.thickness * 1e3)
        
        return {'type': self.type, 'dimensions': {tags[i]: dim[i] for i in range(len(dim))}, 'material': self.plates[0].material}