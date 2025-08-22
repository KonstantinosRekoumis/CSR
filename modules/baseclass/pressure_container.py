from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.utils.constants import verify_dynamic_condition
from modules.utils.logger import Logger
from modules.utils.operations import normals_2d


class PressureContainer:
    def __init__(self, plate: StiffPlate, flip_norm: bool) -> None:
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
        )  # Makes it trivial to gather the pressure later
        self.pressure_grid = self.plate.pressure_grid
        if flip_norm:
            self.pressure_grid = self.pressure_grid[::-1]
        self.evaluator = None
        self.eta = normals_2d(self.pressure_grid)
        self.__pressure_distro = {}
        self.__kc = -1.0

    @property
    def Kc(self) -> float:  # noqa: N802
        if self.__kc == -1.0:
            Logger.error("Accesing the Kc parameter, that is yet to be set!", die=True)
        return self.__kc

    @Kc.setter
    def Kc(self, value: float) -> None:  # noqa: N802
        if isinstance(value, float) and (value >= 0.0):
            self.__kc = value
            return
        Logger.error(f"The value assigned at Kc parameter is invalid! {value=} {type(value)}")

    @property
    def static_pressure(self) -> list[float]:
        if "STATIC" in self.__pressure_distro:
            return self.__pressure_distro["STATIC"]
        Logger.warning(
            f"No static pressure was calculated for {self.plate} in {self.block}"
        )
        Logger.warning("Returning Zeros!")
        return self.unif_distr(magn=0)

    @static_pressure.setter
    def static_pressure(self, value: list[float]) -> None:
        self.__pressure_distro["STATIC"] = value

    def dynamic_pressure(self, key: str) -> list[float]:
        if "STATIC" : return self.static_pressure #for the occasional bozo (me)
        _ = verify_dynamic_condition(key)
        if key in self.__pressure_distro:
            return self.__pressure_distro[key]
        Logger.warning(
            f"No dynamic pressure for condition : {key} was \
                        calculated for {self.plate} in {self.block}"
        )
        Logger.warning("Returning Zeros!")
        return self.unif_distr(0)

    def set_dynamic_press(self, cond: str, values: list[float]) -> None:
        _ = verify_dynamic_condition(cond)
        self.__pressure_distro[cond] = values

    def unif_distr(self, magn: float) -> list[float]:
        return [magn] * len(self.pressure_grid)
