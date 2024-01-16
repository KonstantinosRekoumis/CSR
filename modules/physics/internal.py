from modules.baseclass.block import Block, SpaceType
from modules.physics.data import Data
from modules.physics.operations import hydrostatic_pressure
from modules.utils.constants import G
from modules.utils.logger import Logger


def static_liquid_pressure(block: Block):
    """
    Static Liquid Pressure : Normal Operations at sea and Harbour/Sheltered water operations\n
    To access the Normal Operations at sea component use the key 'S-NOS' and the key 'S-HSWO' for the \n
    Harbour/Sheltered water operations.

    """
    # Ppv : Design vapour Pressure not to be taken less than 25 kPa
    # When the Code is made universal for Dry and Tankers it shall be taken to consideration
    # For the time is left as it is. IF AN LC BLOCK IS CREATED THE RESULT WILL BE USELESS
    if block.space_type is SpaceType.DryCargo:
        return [None, None]

    P_nos = [None] * len(block.pressure_coords)
    P_hswo = [None] * len(block.pressure_coords)
    Ztop = max(block.coords, key=lambda x: x[1])[1]

    if block.space_type is SpaceType.LiquidCargo:
        F_nos = lambda z: hydrostatic_pressure(z, Ztop, max(block.payload['rho'], 1.025)) + block.payload['Ppv']
    else:
        F_nos = lambda z: hydrostatic_pressure(z, (Ztop + block.payload['hair'] / 2), max(block.payload['rho'], 1.025))

    for i, point in enumerate(block.pressure_coords):
        P_nos[i] = F_nos(point[1])

    block.Pressure['STATIC'] = P_nos
    return P_nos


def static_dry_cargo_pressure(block: Block):
    '''
    Static Dry Cargo Pressure: Evaluates the pressure distribution of the static load applied by the cargo to the stiffened plates.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)
    '''

    zc = block.pressure_coords[0][
        1]  # max of the coordinates may be redundant as there is a specific order the plates shall be (clockwise)

    rho = block.payload['rho'] if (block.payload['rho'] >= 1.0) else 1.0

    def static(z, Kc):
        if z <= zc:
            return G * rho * Kc * (block.CG[2] - z)
        else:
            return 0

    P = [None] * len(block.pressure_coords)

    for i, point in enumerate(block.pressure_coords):
        P[i] = static(point[1], block.Kc[i])

    block.Pressure['STATIC'] = P
    return P


def dynamic_liquid_pressure(block: Block, case: Data):
    """
    Dynamic Liquid Pressure: Evaluates the pressure distribution due to the dynamic motion of a fluid inside\n
    a tank.
    """

    def ref_eval(block: Block, a: tuple):
        """
        V j = aX ( xj – x G ) + aY ( y j – y G ) + ( aZ + g ) ( zj – zG )
        """
        Max = 0
        V = lambda x, y, z: a[0] * (x - block.CG[0]) + a[1] * (y - block.CG[1]) + (a[2] + G) * (z - block.CG[2])
        pos = []
        for i, point in enumerate(block.pressure_coords):
            temp = V(*(case.Lsc * case.fxL, *point))
            if temp > Max: pos = point

        # NOTE for some reason here, *pos explosion was used, but no callee actually used any of the values!
        return block.CG[0], pos[0], pos[1]

    ax, ay, az = case.accel_eval(block.CG)  # 221
    x0, y0, z0 = ref_eval(block, (ax, ay, az))

    Logger.debug('ax : ', ax, ' ay : ', ay, ' az : ', az, 'x0 : ', x0, ' y0 : ', y0, ' z0 : ', z0)

    # strength assessment only
    if block.space_type is SpaceType.LiquidCargo:
        full_l = 0.62
        full_t = 0.67
    else:
        full_l = 1.0
        full_t = 1.0

    P = [None] * len(block.pressure_coords)
    Pld = lambda x, y, z: case.fb * max(block.payload['rho'], 1.025) * (
            az * (z0 - z) + full_l * ax * (x0 - x) + full_t * ay * (y0 - y))

    for i, point in enumerate(block.pressure_coords):
        P[i] = Pld(*(case.Lsc * case.fxL, *point))

    block.Pressure[case.cond] = P
    return P


def dynamic_dry_cargo_pressure(block: Block, case: Data):
    """
    Dynamic Dry Cargo Pressure: Evaluates the pressure distribution due to the dynamic movements of the ship.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)

    """
    zc = block.pressure_coords[0][
        1]  # max of the coordinates may be redundant as there is a specific order the plates shall be (clockwise)

    rho = block.payload['rho'] if (block.payload['rho'] >= 1.0) else 1.0

    def Pbd(x, y, z, ax, ay, az, Kc):
        if z <= zc:
            return case.fb * rho * (Kc * az * (zc - z) + 0.25 * ax * (block.CG[0] - x) + 0.25 * ay * (block.CG[1] - y))
        else:
            return 0

    ax, ay, az = case.accel_eval(block.CG)  # 221
    P = [None] * len(block.pressure_coords)

    for i, point in enumerate(block.pressure_coords):
        P[i] = Pbd(block.CG[0], *point, ax, ay, az, block.Kc[i])

    block.Pressure[case.cond] = P
    return P


def void_pressure(block: Block, case: Data):
    P = [0] * len(block.pressure_coords)
    block.Pressure[case.cond] = P
    block.Pressure['STATIC'] = P
    return P
