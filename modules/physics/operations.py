from modules.utils.constants import G
from modules.utils.logger import Logger


def hydrostatic_pressure(z: float, Zmax: float, rho: float):
    """
    Convention is that the zero is located at the keel plate
    """
    Logger.debug(f"Called with Z:{z} Zmax:{Zmax} rho:{rho}")
    assert z >= 0

    dT = Zmax - z
    return rho * G * dT
