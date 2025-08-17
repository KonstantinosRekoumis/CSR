from modules.utils.constants import G
from modules.utils.logger import Logger


def hydrostatic_pressure(z: float, zmax: float, rho: float)->float:
    """
    Convention is that the zero is located at the keel plate
    """
    Logger.debug(f"Called with Z:{z} Zmax:{zmax} rho:{rho}")
    assert z >= 0

    dT = zmax - z  # noqa: N806
    return rho * G * dT
