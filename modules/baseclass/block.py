import math
from enum import Enum

from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.baseclass.pressure_container import PressureContainer
from modules.utils.constants import HEAVY_HOMO, RHO_F, RHO_S
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger
from modules.utils.operations import d2r, linespace, normals_2d


class SpaceType(Enum):
    WaterBallast = {"rho": RHO_S, "hair": 0.0}
    DryCargo = {"rho": HEAVY_HOMO, "fdc": 1.0, "psi": 30.0}
    LiquidCargo = {"rho": 0.8, "Ppv": 25.0, "fcd": 1.0}
    OilTank = {"rho": 0.8, "hair": 0.0}
    FreshWater = {"rho": RHO_F, "hair": 0.0}
    VoidSpace = {"rho": 0.0, "hair": 0.0}
    Sea = {"rho": RHO_S}
    Atmosphere = {"rho": RHO_S}


LOAD_SPACE_TYPE = {
    "SpaceType.WaterBallast": SpaceType.WaterBallast,
    "SpaceType.DryCargo": SpaceType.DryCargo,
    "SpaceType.LiquidCargo": SpaceType.LiquidCargo,
    "SpaceType.OilTank": SpaceType.OilTank,
    "SpaceType.FreshWater": SpaceType.FreshWater,
    "SpaceType.VoidSpace": SpaceType.VoidSpace,
}


@auto_str
class Block:
    """
    ------------------------------------------
    Block class holds the geometric and physical properties of the various Volumes encountered on a ship.
    Blocks are associated with their boundary plates that give them their geometry.
    Block class is used to represent a Water Ballast / Fuel / Oil (etc.) tank, Dry / Liquid Cargo Space.
    This is done to further enhance the clarity of what substances are in contact with certain plates.
    Currently are supported 5 Volume Categories :
    1) Water Ballast -> type : WB
    2) Dry Cargo -> type: DC
    3) Liquid Cargo -> type: LC
    4) Fuel Oil/ Lube Oil/ Diesel Oil -> type: OIL
    5) Fresh Water -> type: FW
    6) Dry/Void Space -> type: VOID
    ------------------------------------------
    In order to properly calculate the Pressure Distributions the normal Vectors need to be properly evaluated.
    Is considered that the Global Positive Direction is upwards of Keel (z = 0) towards the Main Deck.
    However, the local positive axis are outwards for the internal Tanks and inwards for
    the SEA and ATMosphere Blocks. So, pay attention to the way the plates are inserted and blocks are evaluated.
    It would be preferable to have a counterclockwise plate definition order for shell plates and a clockwise order
    for internal plates. Also, use the minus before each plate id at the input file to address the block's boundary direction on the specified plate.
    For example, a shell plate at Draught has a certain orientation that is uniform with the SEA block
    (the stiffeners (and normals) are facing inwards) while the WB block requires a different direction
    (normals facing outwards). For this purpose, the id in the WB block would be
    -id.
    !!! BE CAREFUL THAT A CLOSED SMOOTH GEOMETRY IS CREATED !!! Verify the block appropriate set up using the
    *block_plot(ship)* and *pressure_plot(ship,'Null','<block tag>')* rendering methods.

        Args:
            name (str): The block name
            symmetrical (bool): If True the block will be mirrored around Zaxis
            space_type (str): The Volume Categorization
            list_plates_id (list[int]): The list of plates geometrically
            defining the volume
    """

    def __init__(
        self,
        name: str,
        symmetrical: bool,
        space_type: SpaceType,
        list_plates_id: list[int],
        *args,
    ) -> None:
        self.name = name
        self.symmetrical = symmetrical  # Symmetry around the Z-axis
        self.space_type = space_type
        self.list_plates_id = list_plates_id
        self.payload = self.space_type.value

        self.coords = []
        self.pressure_coords = []
        self.plates_indices = []  # Holds data for the plate's id at a certain grid point
        self.CG :list[float]= []

        self.eta = []  # Evaluates the normal vectors of each block
        # self.Pressure = {}  # Pass each Load Case index as key and values as a list
        self.pressure_cont: list[PressureContainer] = []
        self.Kc = []
        self.Kc_eval = (
            self.Kc_eval_ if self.space_type is SpaceType.DryCargo else lambda *x: None
        )
        self.max_z = -1000.0

    def Kc_eval_(self, start:list[float], end:list[float], stiff_plate_type:int)->float:  # noqa: N802
        """Kc_eval_
            Function used to evaluate the Kc parameter in the case of dry cargo holds
        Args:
            start (float): _description_
            end (float): _description_
            stiff_plate_type (int): _description_
        """
        try:
            __psi = self.payload["psi"]
        except KeyError:
            Logger.error(
                "The required 'psi' value is missing in the payload declaration."
            )
        def kc(a:float)->float:
            return (math.cos(a) ** 2
                        + (1 - math.sin(d2r(__psi))) * math.sin(a) ** 2)
        if stiff_plate_type not in (3, 5, 4):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            alpha = math.atan2(dy, dx)
            return kc(alpha)
        return 0.0

    def get_coords(self, stiff_plates: list[StiffPlate])->None:
        """
        Get the coordinates of the block from its list of plates. TO BE CALLED AFTER THE BLOCKS ARE VALIDATED!!!
        If the block is not calculated correctly then you need to change the id order in the save file.
        """
        # for i in self.list_plates_id:
        Dx = 0.1
        Mx, My = (0, 0)
        A = 0
        start_p = []
        c = 0
        while c < len(self.list_plates_id):
            for j in stiff_plates:
                if j.id == abs(self.list_plates_id[c]):
                    start = j.plate.start
                    end = j.plate.end
                    flip_norm = False
                    if self.list_plates_id[c] < 0:
                        start = j.plate.end
                        end = j.plate.start
                        flip_norm = True
                    if self.list_plates_id[c]==0:
                        Logger.error("You cannot provide a plate with id 0")
                    self.pressure_cont.append(
                        PressureContainer(j, flip_norm)
                    )
                    if self.space_type is SpaceType.DryCargo:
                        self.pressure_cont[-1].Kc = self.Kc_eval(j.plate.start, j.plate.end, j.tag)
                    self.max_z = max(start[1], end[1], self.max_z)
                    if len(self.coords) != 0:
                        c += 1
                        N = (
                            j.plate.length // Dx
                        )  # Weight the points relative to plate length
                        if start not in self.coords:
                            self.coords.append(start)
                            # self.Kc_eval(start, end, j.tag)
                            self.plates_indices.append(-1)  # Null id
                            Mx += N * start[0] - start_p[0]
                            My += N * start[1] - start_p[1]
                            A += N * 1
                        if end not in self.coords:
                            if j.tag == 4:  # Bilge
                                X, Y = j.plate.render_data()[:2]
                                s = len(X) - 2
                                if self.list_plates_id[c - 1] >= 0:
                                    r_ = range(1, len(X) - 1)
                                elif self.list_plates_id[c - 1] < 0:
                                    r_ = range(len(X) - 2, 0, -1)
                                for i in r_:
                                    self.coords.append((X[i], Y[i]))
                                    # self.Kc_eval(start, end, j.tag)
                                    self.plates_indices.append(j.id)
                                    Mx += N * X[i] / s - start_p[0]
                                    My += N * Y[i] / s - start_p[1]
                                    A += N * 1 / s
                            else:
                                self.coords.append(end)
                                self.Kc_eval(start, end, j.tag)
                                self.plates_indices.append(j.id)
                                Mx += N * end[0] - start_p[0]
                                My += N * end[1] - start_p[1]
                                A += N * 1
                    elif len(self.coords) == 0:
                        # c is not incremented to re-parse the first plate and register its end point
                        self.coords.append(start)
                        # self.Kc_eval(start, end, j.tag)
                        # self.plates_indices.append(j.id)
                        start_p = start
                        A += j.plate.length // Dx

                    break

        self.CG = [Mx / A, My / A] if not self.symmetrical else [0, My / A]

        # self.calculate_pressure_grid(10)
        # self.calculate_CG()

    def calculate_pressure_grid(self, resolution: int):
        """
        Create a 1D computational mesh to calculate the loads pressure distributions.
        Simply calculating with the geometric coordinates does not hold enough precision.
        The pressure coordinates are calculated on a standard Ds between two points using linear interpolation.
        TODO: offload this elsewhere. Eventhough it is generated adequately here, there is an implicit mapping between
            pressure grid coords and plate elements that makes it cumbersome to offload the pressure distribution.
        """
        K = []
        P = []
        temp = linespace(1, resolution, 1)
        Kc_not_None = True if self.space_type is SpaceType.DryCargo else False
        for i in range(len(self.coords) - 1):
            # eliminate duplicate entries -> no problems with normal vectors
            if self.coords[i] not in self.pressure_coords:
                self.pressure_coords.append(self.coords[i])
                if Kc_not_None:
                    K.append(self.Kc[i])
            dy = self.coords[i + 1][1] - self.coords[i][1]
            dx = self.coords[i + 1][0] - self.coords[i][0]
            span = math.sqrt(dy**2 + dx**2)
            phi = math.atan2(dy, dx)
            for j in temp:
                self.pressure_coords.append(
                    (
                        self.coords[i][0] + span / resolution * j * math.cos(phi),
                        self.coords[i][1] + span / resolution * j * math.sin(phi),
                    )
                )
                P.append(self.plates_indices[i])
                if Kc_not_None:
                    K.append(self.Kc[i])
            self.pressure_coords.append(self.coords[i + 1])
            P.append(self.plates_indices[i])
            if Kc_not_None:
                K.append(self.Kc[i + 1])

        self.plates_indices = P
        if Kc_not_None:
            self.Kc = K
        self.eta = normals_2d(self.pressure_coords)

    def render_data(self) -> tuple[list[float], list[float], SpaceType, list[float]]:
        x = [i[0] for i in self.coords]
        y = [i[1] for i in self.coords]
        x.append(x[0])
        y.append(y[0])
        return x, y, self.space_type, self.CG[1:]

    def pressure_data(
        self, pressure_index: str, graphical: bool = False
    ) -> tuple[list[float], list[float], list[float]]:
        """
        Returns the Pressure Data for plotting or file output.
        Note that graphical will force ONES over the actual Data.
        """
        x, y, p = [], [], []

        for cont in self.pressure_cont[:-1]:
            x = [*x, *[i[0] for i in cont.pressure_grid[:-1]]]
            y = [*y, *[i[1] for i in cont.pressure_grid[:-1]]]
            __p = (
                cont.dynamic_pressure(pressure_index)
                if not graphical
                else cont.unif_distr(1.0)
            )
            p = [*p, *__p[:-1]]

        cont = self.pressure_cont[-1]

        x = [*x, *[i[0] for i in cont.pressure_grid]]
        y = [*y, *[i[1] for i in cont.pressure_grid]]
        __p = (
            cont.dynamic_pressure(pressure_index)
            if not graphical
            else cont.unif_distr(1.0)
        )
        p = [*p, *__p]


        return x, y, p

    def pressure_over_plate(self, stiff_plate: StiffPlate, pressure_index:str
                            ) -> list[tuple[float, ...]] | None:
        for tmp in self.pressure_cont:
            if tmp.plate.id == stiff_plate.id:
                press_distr = tmp.dynamic_pressure(pressure_index)
                return [
                    (*tmp.pressure_grid[i], *tmp.eta[i], press_distr[i])
                    for i in range(len(tmp.pressure_grid))
                ]
        Logger.warning(
            f"Requesting pressure over plate {stiff_plate} "
            f"that does not belong in the block {self}. Returning None"
        )
        return None
