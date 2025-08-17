import math

from modules.baseclass.block import Block, SpaceType
from modules.physics.operations import hydrostatic_pressure
from modules.utils.constants import G
from modules.utils.logger import Logger
from modules.utils.operations import lin_int_dict


def block_hydrostatic_pressure(block: Block, Tlc: float, rho: float) -> None:  # noqa: N803
    """
    Evaluation of hydrostatic pressure for SEA block
    """

    def evaluate(pressure_coords: list) -> list[float]:
        p = p_c.unif_distr(magn=0)
        for i, point in enumerate(pressure_coords):
            if point[1] <= Tlc:
                p[i] = hydrostatic_pressure(point[1], Tlc, rho)
        return p

    if block.space_type is SpaceType.Sea:
        for p_c in block.pressure_cont:
            p_c.static_pressure = evaluate(p_c.pressure_grid)
        return

    Logger.warning(f"Does not support block of type {block.space_type!s}")


def hsm_wave_pressure(cons_: list[float], _1_: bool, block: Block) -> None:
    """
    Calculates the wave pressure in kPa over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the HSM-1 or HSM-2, taking the values True and False respectively
    """
    fnl = 0.9  # @50% Lbp pp 197

    fxL, fps, fbeta, ft, rho, LBP, B, Cw, Lsc, Tlc, D = cons_  # noqa: N806

    fh = 3 * (1.21 - 0.66 * ft)

    kp = {
        0: lambda fyb_: -0.25 * ft * (1 + fyb_),
        round(0.3 - 0.1 * ft, 4): -1,
        round(0.35 - 0.1 * ft, 4): 1,
        round(0.8 - 0.2 * ft, 4): 1,
        round(0.9 - 0.2 * ft, 4): -1,
        1.0: -1,
    }

    kp_c = 0

    ka = 1.0  # @50% Lbp, may introduced the entire formula later

    fyB = lambda x: 2 * x / B
    fyz = lambda y, z: z / Tlc + fyB(y) + 1

    def Phs(y: float, z: float) -> float:  # noqa: N802
        l = 0.6 * (1 + ft) * LBP  # noqa: E741
        return (
            fbeta * fps * fnl * fh * fyz(y, z) * ka * kp_c * Cw
            * math.sqrt((l + max(Lsc, 110) - 125) / Lsc)
        )

    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    alpha = -1 if _1_ else 1
    key = "HSM-1" if _1_ else "HSM-2"
    # Weatherdeck has special rules according to Section 5.2.2
    if ( block.space_type is SpaceType.Sea):
        for container in block.pressure_cont:
            pw = [0.0] * len(container.pressure_grid)
            for i, point in enumerate(container.pressure_grid):
                kp_c = lin_int_dict(kp, fxL, fyB(point[0]), suppress=True)
                hw = alpha * Phs(B / 2, Tlc) / rho / G  # wave height
                if point[1] < Tlc:
                    pw[i] = max(
                        alpha * Phs(*point), -hydrostatic_pressure(point[1], Tlc, rho)
                    )
                elif point[1] < Tlc + hw:
                    # PW = PW,WL - ρg(z - TLC)  # noqa: RUF003
                    pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
            container.set_dynamic_press(key, pw)
        return
    if block.space_type is SpaceType.Atmosphere:
        x = 1.0  # Section 5.2.2.4, Studying only the weather deck
        Pmin = 14.9 + 0.195 * LBP  # noqa: N806
        if LBP >= 100:  # noqa: PLR2004
            Pmin = 34.3  # xl = 0.5  # noqa: N806
        kp_c = lin_int_dict(kp, fxL, fyB(B), suppress=True)
        hw = alpha * Phs(B / 2, Tlc) / rho / G
        for container in block.pressure_cont:
            pw = [0.0] * len(container.pressure_grid)
            for i, point in enumerate(container.pressure_grid):
                if Tlc <= point[1] < Tlc + hw:
                    pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                pw[i] = max(pw[i], Pmin)
                pw[i] *= x
            container.set_dynamic_press(key, pw)
        return
    Logger.error("Cannot evaluate External pressures for an internal block.")


def bsp_wave_pressure(cons_: list[float], _1_: bool, block: Block, port:bool=True)->None:  # noqa: E501
    """
    Calculates the wave pressure over a plate according to Part 1 Chapter 4, Section 5.
    _1_ -> indicates whether we are interested in the BSP-1 or BSP-2, taking the values True and False respectively
    Port -> indicates whether we are working on the Port or Starboard side, taking the values True and False respectively
    """
    # for the time being it can be left like this as a symmetrical case focused on Port
    key = "BSP-1P" if _1_ else "BSP-2P"
    if not port:
        Logger.error("Dont mess with the Port Setting for the time being...")
        key = "BSP-1S" if _1_ else "BSP-2S"

    fnl = 0.8  # @50% Lbp pp 202

    fxL, fps, fbeta, ft, rho, LBP, B, Cw, Lsc, Tlc, D = cons_  # noqa: N806

    l = 0.2 * (1 + 2 * ft) * LBP

    fyB = lambda y: 2 * y / B  # noqa: N806
    fyz = lambda y, z: 2 * z / Tlc + 2.5 * fyB(y) + 0.5  # worst case scenario

    Pbsp = ( lambda y, z: 4.5 * fbeta * fps * fnl * fyz(y, z) * Cw  # noqa: N806
            * math.sqrt((l + Lsc - 125) / LBP)
    )

    alpha = 1 if _1_ else -1
    # Weatherdeck has special rules according to Section 5.2.2
    if block.space_type is SpaceType.Sea:
        hw = alpha * Pbsp(B / 2, Tlc) / rho / G
        for cont in block.pressure_cont:
            pw = cont.unif_distr(magn=0)
            for i, point in enumerate(cont.pressure_grid):
                if point[1] < Tlc:
                    pw[i] = max(
                        alpha * Pbsp(*point),
                        -hydrostatic_pressure(point[1], Tlc, rho / G)
                    )
                elif Tlc <= point[1] < Tlc + hw:
                    pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho / G)
            cont.set_dynamic_press(key, pw)
        return
    if block.space_type is SpaceType.Atmosphere:
        x = 1.0  # Section 5.2.2.4, Studying only the weather deck
        Pmin = 14.9 + 0.195 * LBP  # noqa: N806
        if LBP >= 100:  # noqa: PLR2004
            Pmin = 34.3  # xl = 0.5  # noqa: N806
        hw = alpha * Pbsp(B / 2, Tlc) / rho / G
        for cont in block.pressure_cont:
            pw = cont.unif_distr(magn=0)
            for i, point in enumerate(cont.pressure_grid):
                if Tlc <= point[1] < Tlc + hw:
                    pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                    pw[i] = max(pw[i], Pmin)
                pw[i] *= x
            cont.set_dynamic_press(key, pw)
        return
    Logger.error("Cannot evaluate External pressures for an internal block.")
