import math

from modules.baseclass.block import Block
from modules.physics.operations import hydrostatic_pressure
from modules.utils.constants import G
from modules.utils.logger import Logger
from modules.utils.operations import lin_int_dict


def block_hydrostatic_pressure(block: Block, Tlc: float, rho: float):
    """
    Evaluation of hydrostatic pressure for SEA block
    """
    P = [0] * len(block.pressure_coords)
    if block.space_type == 'SEA':
        for i, point in enumerate(block.pressure_coords):
            if point[1] <= Tlc:
                P[i] = hydrostatic_pressure(point[1], Tlc, rho)
        block.Pressure['STATIC'] = P
    else:
        Logger.warning(f'Does not support block of type {block.space_type}')
        pass
    return P


def hsm_wave_pressure(cons_: list[float], _1_: bool, block: Block):
    """
    Calculates the wave pressure in kPa over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the HSM-1 or HSM-2, taking the values True and False respectively
    """
    fnl = 0.9  # @50% Lbp pp 197

    fxL, fps, fbeta, ft, rho, LBP, B, Cw, Lsc, Tlc, D = cons_

    fh = 3 * (1.21 - 0.66 * ft)

    kp = {
        0: lambda fyb_: -0.25 * ft * (1 + fyb_),
        round(0.3 - 0.1 * ft, 4): -1,
        round(0.35 - 0.1 * ft, 4): 1,
        round(0.8 - 0.2 * ft, 4): 1,
        round(0.9 - 0.2 * ft, 4): -1,
        1.0: -1
    }

    kp_c = 0

    ka = 1.0  # @50% Lbp, may introduced the entire formula later
    l = 0.6 * (1 + ft) * LBP

    fyB = lambda x: 2 * x / B
    fyz = lambda y, z: z / Tlc + fyB(y) + 1

    Phs = lambda y, z: fbeta * fps * fnl * fh * fyz(y, z) * ka * kp_c * Cw * math.sqrt((l + max(Lsc, 110) - 125) / Lsc)

    Pw = [None] * len(block.pressure_coords)
    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))

    if block.space_type == 'SEA':  # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            for i, point in enumerate(block.pressure_coords):  # the last 3 coordinates pressure_are rent
                kp_c = lin_int_dict(kp, fxL, fyB(point[0]), suppress=True)
                # print(f'kp_c: {kp_c}')
                hw = -1 * Phs(B / 2, Tlc) / rho / G
                if point[1] < Tlc:
                    Pw[i] = max(-1 * Phs(*point), -hydrostatic_pressure(point[1], Tlc, rho))
                elif Tlc <= point[1] < Tlc + hw:
                    Pw[i] = Phs(point[0], Tlc) + hydrostatic_pressure(point[1], Tlc, rho)  # PW = PW,WL - ρg(z - TLC)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)  # PW = PW,WL - ρg(z - TLC)
                    # print('------ Tlc < x < Tlc+hw----')
                    # print("Wave height : ",hw)
                    # print("Pw,wl : ",hw*rho*G)
                    # print("Hydrostatic Pressure : ",hydrostatic_pressure(point[1],Tlc,rho))
                    # print('---------------------------')
                else:
                    Pw[i] = 0
        else:
            for i, point in enumerate(block.pressure_coords):
                kp_c = lin_int_dict(kp, fxL, fyB(point[0]), suppress=True)
                hw = Phs(B / 2, Tlc) / rho / G
                if point[1] < Tlc:
                    Pw[i] = max(Phs(*point), -hydrostatic_pressure(point[1], Tlc, rho))
                elif Tlc <= point[1] < Tlc + hw:
                    Pw[i] = Phs(point[0], Tlc) + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                else:
                    Pw[i] = 0

    elif block.space_type == 'ATM':
        x = 1.0  # Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3  # xl = 0.5
        else:
            Pmin = 14.9 + 0.195 * LBP

        kp_c = lin_int_dict(kp, fxL, fyB(D), suppress=True)
        if _1_:
            hw = -1 * Phs(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if Tlc <= point[1] < Tlc + hw:
                    Pw[i] = Phs(point[0], Tlc) + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = max(Pw[i], Pmin)
                else:
                    Pw[i] = 0
                    Pw[i] = max(Pw[i], Pmin)
                Pw[i] *= x
        else:
            hw = Phs(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if Tlc <= point[1] < Tlc + hw:
                    Pw[i] = Phs(point[0], Tlc) + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = max(Pw[i], Pmin)
                else:
                    Pw[i] = 0
                    Pw[i] = max(Pw[i], Pmin)
                Pw[i] *= x

    else:
        Logger.warning('Cannot evaluate External pressures for an internal block.')
    key = 'HSM-1' if _1_ else 'HSM-2'
    block.Pressure[key] = Pw
    return Pw


def bsp_wave_pressure(cons_: list[float], _1_: bool, block: Block, Port=True):
    """
    Calculates the wave pressure over a plate according to Part 1 Chapter 4, Section 5.
    _1_ -> indicates whether we are interested in the BSP-1 or BSP-2, taking the values True and False respectively
    Port -> indicates whether we are working on the Port or Starboard side, taking the values True and False respectively
    """
    # for the time being it can be left like this as a symmetrical case focused on Port
    if not Port:
        Logger.error('Dont mess with the Port Setting for the time being...')

    fnl = 0.8  # @50% Lbp pp 202

    fxL, fps, fbeta, ft, rho, LBP, B, Cw, Lsc, Tlc, D = cons_

    l = 0.2 * (1 + 2 * ft) * LBP

    fyB = lambda y: 2 * y / B
    fyz = lambda y, z: 2 * z / Tlc + 2.5 * fyB(y) + 0.5  # worst case scenario

    Pbsp = lambda y, z: 4.5 * fbeta * fps * fnl * fyz(y, z) * Cw * math.sqrt((l + Lsc - 125) / LBP)

    Pw = [None] * len(block.pressure_coords)
    if block.space_type == 'SEA':  # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            hw = Pbsp(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if point[1] < Tlc:
                    Pw[i] = max(Pbsp(*point), -hydrostatic_pressure(point[1], Tlc, rho / G))
                elif Tlc <= point[1] < Tlc + hw:
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho / G)
                else:
                    Pw[i] = 0
        else:
            hw = -Pbsp(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if point[1] < Tlc:
                    Pw[i] = max(-Pbsp(*point), -hydrostatic_pressure(point[1], Tlc, rho))
                elif Tlc <= point[1] < Tlc + hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                else:
                    Pw[i] = 0
    elif block.space_type == 'ATM':
        x = 1.0  # Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3  # xl = 0.5
        else:
            Pmin = 14.9 + 0.195 * LBP

        hw = Pbsp(B / 2, Tlc) / rho / G
        if _1_:
            hw = Pbsp(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if Tlc <= point[1] < Tlc + hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = max(Pw[i], Pmin)
                else:
                    Pw[i] = 0
                Pw[i] *= x
        else:
            hw = -Pbsp(B / 2, Tlc) / rho / G
            for i, point in enumerate(block.pressure_coords):
                if Tlc <= point[1] < Tlc + hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw * rho * G + hydrostatic_pressure(point[1], Tlc, rho)
                    Pw[i] = max(Pw[i], Pmin)
                else:
                    Pw[i] = 0
                Pw[i] *= x
    if Port:
        key = 'BSP-1P' if _1_ else 'BSP-2P'
    else:
        key = 'BSP-1S' if _1_ else 'BSP-2S'

    block.Pressure[key] = Pw
    return Pw
