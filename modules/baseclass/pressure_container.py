from baseclass.block import Block
from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.utils.logger import Logger
from modules.utils.operations import normals_2d
from physics.data import _check_cond


class PressureContainer:
    def __init__(self, plate: StiffPlate, block: Block, flip_norm: bool) -> None:
        """
        What I want from this:
           An explicit way to map Pressure Distributions to plates,
            without overloading with information the plate.
            Maybe it can enable the file output of the distributions as well.


        Args:
            plate (StiffPlate): The stiff plate whose pressure distributions are stored
            block (Block): The Block containing the Pressure Container
        """
        self.plate = plate
        self.plate.pressure_containers.append(
            self
        )  # Makes trivial to gather the pressure later
        self.block = block
        self.pressure_grid = self.plate.pressure_grid
        if flip_norm:
            self.pressure_grid = self.pressure_grid[::-1]
        self.evaluator = None
        self.eta = normals_2d(self.pressure_grid)
        self.__pressure_distro = {}
        self.Kc = self.block.Kc_eval(
            self.pressure_grid[0], self.pressure_grid[-1], self.plate.tag
        )

    @property
    def static_pressure(self) -> list[float]:
        if "STATIC" in self.__pressure_distro:
            return self.__pressure_distro["STATIC"]
        Logger.warning(
            f"No static pressure was calculated for {self.plate} in {self.block}"
        )
        Logger.warning("Returning Zeros!")
        return self.unit_distr(magn=0)

    @static_pressure.setter
    def static_pressure(self, value: list[float]) -> None:
        self.__pressure_distro["STATIC"] = value

    def dynamic_pressure(self, key: str) -> list[float]:
        _ = _check_cond(key)
        if key in self.__pressure_distro:
            return self.__pressure_distro[key]
        Logger.warning(
            f"No dynamic pressure for condition : {key} was \
                        calculated for {self.plate} in {self.block}"
        )
        Logger.warning("Returning Zeros!")
        return self.unit_distr(magn=0)

    def set_dynamic_press(self, cond: str, values: list[float]) -> None:
        _ = _check_cond(cond)
        self.__pressure_distro[cond] = values

    def unit_distr(self, magn:float=1.0, *args):  # noqa: ARG002
        return [magn]*len(self.pressure_grid)


