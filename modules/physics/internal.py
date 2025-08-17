from modules.baseclass.block import Block, SpaceType
from modules.baseclass.pressure_container import PressureContainer
from modules.physics.data import Data
from modules.physics.operations import hydrostatic_pressure
from modules.utils.constants import G
from modules.utils.logger import Logger


def static_liquid_pressure(block: Block) -> None:
    """
    Static Liquid Pressure : Normal Operations at sea and Harbour/Sheltered water operations\n
    To access the Normal Operations at sea component use the key 'S-NOS' and the key 'S-HSWO' for the \n
    Harbour/Sheltered water operations.

    """
    # Ppv : Design vapour Pressure not to be taken less than 25 kPa
    # When the Code is made universal for Dry and Tankers it shall be taken to consideration
    # For the time is left as it is. IF AN LC BLOCK IS CREATED THE RESULT WILL BE USELESS (? TODO: Fix this)
    if block.space_type is SpaceType.DryCargo:
        return

    P_nos = []  # noqa: N806
    P_hswo = []  # noqa: N806
    ztop = block.max_z

    if block.space_type is SpaceType.LiquidCargo:
        F_nos = lambda z: hydrostatic_pressure(z, ztop, max(block.payload["rho"], 1.025)) + block.payload["Ppv"]  # noqa: E501, N806
    else:
        F_nos = lambda z: hydrostatic_pressure(z, (ztop + block.payload["hair"] / 2), max(block.payload["rho"], 1.025))  # noqa: E501, N806

    for pc in block.pressure_cont:
        for i, point in enumerate(pc.pressure_grid):
            P_nos[i] = F_nos(point[1])
        pc.static_pressure = P_nos


def static_dry_cargo_pressure(block: Block) -> None:
    """
    Static Dry Cargo Pressure: Evaluates the pressure distribution of the static load applied by the cargo to the stiffened plates.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)
    """

    zc = block.max_z   # max of the coordinates may be redundant as there is a specific order the plates shall be (clockwise)

    rho = max(block.payload["rho"], 1.0)

    def static(z:float, kc:float)->float:
        if z <= zc:
            return G * rho * kc * (block.CG[2] - z)
        return 0.

    for cont in block.pressure_cont:
        p = cont.unif_distr(0.0)
        __kc = cont.Kc
        assert isinstance(__kc, float), f"FATAL: A dry-cargo block has not a valid {cont.Kc=} value. {cont=}"  # noqa: E501
        for i, point in enumerate(cont.pressure_grid):
            p[i] = static(point[1], __kc)
        cont.static_pressure=p


def dynamic_liquid_pressure(block: Block, case: Data) -> None:
    """
    Dynamic Liquid Pressure: Evaluates the pressure distribution due to the dynamic motion of a fluid inside\n
    a tank.
    """
    ax, ay, az = case.accel_eval(block.CG)  # 221

    """
    V j = aX ( xj - x G ) + aY ( y j - y G ) + ( aZ + g ) ( zj - zG )
    """
    _max = 0
    V = lambda x, y, z: (ax * (x - block.CG[0])
                        + ay * (y - block.CG[1])
                        + (az + G) * (z - block.CG[2]))
    point0 = []
    for cont in block.pressure_cont:
        for point in cont.pressure_grid:
            temp = V(*(case.Lsc * case.fxL, *point))
            if temp > _max: point0 = point  # noqa: E701

    y0, z0 = point0
    x0 = block.CG[0] # TODO: We Consider only extruded along x-axis tanks

    Logger.debug("ax : ", ax, " ay : ", ay, " az : ", az,
                 "x0 : ", x0, " y0 : ", y0, " z0 : ", z0)

    # strength assessment only
    if block.space_type is SpaceType.LiquidCargo:
        full_l = 0.62
        full_t = 0.67
    else:
        full_l = 1.0
        full_t = 1.0

    Pld = lambda x, y, z: case.fb * max(block.payload["rho"], 1.025) * (
            az * (z0 - z) + full_l * ax * (x0 - x) + full_t * ay * (y0 - y))

    for cont in block.pressure_cont:
        p = cont.unif_distr(0.0)
        for i, point in enumerate(cont.pressure_grid):
            p[i] = Pld(*(case.Lsc * case.fxL, *point))
        cont.set_dynamic_press(case.cond, p)



def dynamic_dry_cargo_pressure(block: Block, case: Data)->None:
    """
    Dynamic Dry Cargo Pressure: Evaluates the pressure distribution due to the dynamic movements of the ship.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)

    """
    zc = block.max_z
    rho = max(block.payload["rho"], 1.0)

    def pbd(point:list[float], a_vec:list[float], Kc:float)->float:  # noqa: N803
        x, y, z = point
        ax, ay, az = a_vec
        if z <= zc:
            return (case.fb * rho * (Kc * az * (zc - z)
                    + 0.25 * ax * (block.CG[0] - x)
                    + 0.25 * ay * (block.CG[1] - y)))
        return 0.0

    a_vec = case.accel_eval(block.CG)  # 221

    for cont in block.pressure_cont:
        p = cont.unif_distr(0)
        for i, point in enumerate(cont.pressure_grid):
            p[i] = pbd((block.CG[0], *point), a_vec, block.Kc[i])
        cont.set_dynamic_press(case.cond, p)


def void_pressure(block: Block, case: Data) -> None:
    for cont in block.pressure_cont:
        cont.static_pressure = cont.unif_distr(magn=0)
        cont.set_dynamic_press(case.cond, cont.unif_distr(magn=0))
