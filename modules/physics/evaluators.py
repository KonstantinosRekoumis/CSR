from modules.baseclass.block import SpaceType
from modules.baseclass.ship import Ship
from modules.physics.data import Data
from modules.physics.environmental import block_hydrostatic_pressure
from modules.physics.internal import (
    dynamic_dry_cargo_pressure,
    dynamic_liquid_pressure,
    static_dry_cargo_pressure,
    static_liquid_pressure,
    void_pressure,
)
from modules.utils.logger import Logger


def dynamic_total_eval(ship: Ship, Tlc: float, case: str) -> tuple[Data, Data]:  # noqa: N803
    _1, _2 = "-1", "-2"
    if case in ("BSR", "BSP", "OSA", "OST"):
        _1, _2 = "-1P", "-2P"

    case_1 = Data(Tlc, ship, case + _1)
    case_2 = Data(Tlc, ship, case + _2)
    for c in (case_1, case_2):
        for i in ship.blocks:
            args = (i, c)
            if i.space_type in (SpaceType.Atmosphere, SpaceType.Sea):
                func = c.wave_pressure
                args = (c.external_loadsC(), "1" in c.cond, i)
            elif i.space_type is SpaceType.DryCargo:
                func = dynamic_dry_cargo_pressure
            elif i.space_type in (SpaceType.WaterBallast,
                                  SpaceType.LiquidCargo,
                                  SpaceType.OilTank,
                                  SpaceType.FreshWater):
                func = dynamic_liquid_pressure
            elif i.space_type is SpaceType.VoidSpace:
                func = void_pressure

            pd = func(*args)
            if None not in Pd:
                Logger.debug(f"{c.cond} CASE STUDY:\nCalculated block: ", i.name)
                Logger.debug(" ---- X ----  ---- Y ----  ---- P ----")
                for j in range(len(Pd)):
                    Logger.debug(
                        f"{round(i.pressure_coords[j][0], 4): =11f} "
                        f"{round(i.pressure_coords[j][1], 4): =11f} "
                        f"{round(Pd[j], 4): =11f}"
                    )
    return case_1, case_2


def static_total_eval(ship: Ship, Tlc: float, rho: float):
    for b in ship.blocks:
        if b.space_type is SpaceType.Sea:
            F = block_hydrostatic_pressure
            args = (b, Tlc, rho)
        elif b.space_type is SpaceType.DryCargo:
            F = static_dry_cargo_pressure
            args = (b, )
        elif b.space_type is SpaceType.Atmosphere:
            continue
        elif b.space_type in (SpaceType.WaterBallast,
                              SpaceType.LiquidCargo,
                              SpaceType.OilTank,
                              SpaceType.FreshWater):
            F = static_liquid_pressure
            args = (b, )
        elif b.space_type is SpaceType.VoidSpace: continue

        Pd = F(*args)
        if None not in Pd:
            Logger.debug("STATIC CASE STUDY:\nCalculated block: ", b.name)
            Logger.debug(" ---- X ----  ---- Y ----  ---- P ----")
            for j in range(len(Pd)):
                Logger.debug(
                    f"{round(b.pressure_coords[j][0], 4): =11f} "
                    f"{round(b.pressure_coords[j][1], 4): =11f} "
                    f"{round(Pd[j], 4): =11f}"
                )
