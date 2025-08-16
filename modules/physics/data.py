import math

from modules.baseclass.ship import Ship
from modules.physics.environmental import bsp_wave_pressure, hsm_wave_pressure
from modules.utils.constants import RHO_S, G
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger
from modules.utils.operations import d2r, lin_int_dict

DYNAMIC_CONDITIONS_TAGS = [ "HSM-1", "HSM-2",
                            "HSA-1", "HSA-2",
                            "FSM-1", "FSM-2",
                            "BSR-1P", "BSR-2P",
                            "BSP-1P", "BSP-2P",
                            "OST-1P", "OST-2P",
                            "OSA-1P", "OSA-2P"]

def _check_cond(cond: str)->str|None:
    if cond in DYNAMIC_CONDITIONS_TAGS:
        return cond
    Logger.error(f"""{cond} is not a valid Dynamic Condition abbreviation.
                Invalid condition to study. Enter an appropriate Condition out of :
                {[f"{i}" for i in DYNAMIC_CONDITIONS_TAGS]}
                Currently supported conditions are : HSM and BSP.
                The other conditions will result in invalid results
                The Program Terminates...""", rethrow=KeyError)
    raise RuntimeError



@auto_str
class Data:
    # RIP PhysicsData. Best Class name ever 2022 - 2023 @Navarx0s misses you
    """
    -------------------------------------------------------------------------------------------------------------------
    PhysicsData: Class that holds each different simulation scenario data to pass to the appropriate
    pressure evaluation functions.
    For the Proper Scenario parameters go to pages 181-182\n
    For the kr_p and GM_p parameters use the percentages of tables 1,2 in pages 181-182 they default for Full Load Homogeneous Loading\n
    fbk needs more
    -------------------------------------------------------------------------------------------------------------------
    """
    def __init__(self, tlc: float, ship: Ship, cond: str, rho=RHO_S, kr_p=.35, gm_p=0.12, fbk=1.2):
        # Ship Data and General Data
        # The dynamic condition we are interested in
        self.cond = _check_cond(cond)

        self.Tlc = tlc
        self.rho = rho
        self.LBP = ship.LBP
        self.B = ship.B
        self.Cw = ship.Cw
        self.Lsc = ship.Lsc
        self.Cb = ship.Cb
        self.D = ship.D
        self.a0 = ship.a0
        self.Iyy = ship.Iyy
        self.Ixx = ship.Ixx
        self.yn = ship.yo
        self.xn = ship.xo
        # Universal Coefficients
        self.fxL = 0.5  # As the middle section is the object of study
        self.fps = 1.0  # Extreme Loads Scenario pp. 180 (to fill the other cases)

        if self.Tlc > ship.Tsc:
            Logger.error("Your current Draught must not exceed the Scantling Draught.\n The program Terminates....")
        self.ft = self.Tlc / ship.Tsc
        self.ft = max(self.ft, 0.5)
        self.fbeta = {
            "HSM-1": 1.05, "HSM-2": 1.05,
            "HSA-1": 1.00, "HSA-2": 1.00,
            "FSM-1": 1.05, "FSM-2": 1.05,
            "BSR-1P": 0.80, "BSR-2P": 0.80,
            "BSP-1P": 0.80, "BSP-2P": 0.80,
            "OST-1P": 1.00, "OST-2P": 1.00,
            "OSA-1P": 1.00, "OSA-2P": 1.00,
        }  # pp. 186 Part 1 Chapter 4, Section 4
        self.fb = self.fbeta[self.cond]
        self.flp = 1.0 if (self.fxL >= 0.5) else -1.0
        # roll angle
        self.T_theta = (2.3 * math.pi * kr_p * self.B) / math.sqrt(G * gm_p * self.B)
        self.theta = (9000 * (1.25 - 0.025 * self.T_theta) * self.fps * fbk) / ((self.B + 75) * math.pi)  # deg
        # pitch angle
        self.T_phi = math.sqrt((math.pi * 1.2 * (1 + self.ft) * self.Lsc) / G)
        self.phi = 1350 * self.fps * self.Lsc ** (-0.94) * (1.0 + (2.57 / math.sqrt(G * self.Lsc)) ** 1.2)  # deg
        # Acceleration at the center of Gravity [m/s^2]
        self.a_surge = 0.2 * self.fps * self.a0 * G
        self.a_sway = 0.3 * self.fps * self.a0 * G
        self.a_heave = self.fps * self.a0 * G
        self.a_pitch = self.fps * ((3.1 / math.sqrt(G * self.Lsc)) + 1) * self.phi * math.pi / 180 * (
                2 * math.pi / self.T_phi) ** 2
        self.a_roll = self.fps * self.theta * math.pi / 180 * (2 * math.pi / self.T_theta) ** 2
        self.flp_osa_d = {"< 0.4": -(0.2 + 0.3 * self.ft),
                          "[0.4,0.6]": (-(0.2 + 0.3 * self.ft)) * (5.6 - 11.5 * self.fxL),
                          "> 0.6": 1.3 * (0.2 + 0.3 * self.ft)}
        self.flp_ost_d = {"< 0.2": 5 * self.fxL, "[0.2,0.4]": 1.0, "[0.4,0.65]": -7.6 * self.fxL + 4.04,
                          "[0.65,0.85]": -0.9, "> 0.85": 6 * (self.fxL - 1)}
        # as fxl = 0.5
        self.flp_osa = self.flp_osa_d["[0.4,0.6]"]
        self.flp_ost = self.flp_ost_d["[0.4,0.65]"]
        self.wave_pressure = 0
        self.wave_pressure_functions()
        self.Cwv, self.Cqw, self.Cwh, self.Cwt, self.Cxs, self.Cxp, self.Cxg, self.Cys, self.Cyr, self.Cyg, self.Czh, self.Czr, self.Czp = self.Combination_Factors()
        # Bending Moments and Shear Forces calculation
        self.Mwv_lc, self.Qwv_lc, self.Mwh_lc, self.Mws = self.moments_eval()  # maybe later add torsional calculations
        self.sigma = lambda y, z: 1e-3 * (
                (self.Mwv_lc + self.Mws) / self.Ixx * (z - self.yn) - self.Mwh_lc / self.Iyy * y)

    def external_loadsC(self):
        """
        -------------------------------------------------------------------------------------------------------------------
        Function that returns data for the constants that need to be passed to the external forces calculating functions.
        Output:\n
            A tuple containing:
            fxL, fps, fb, ft,\n
            rho -> <float> Target water's density (default : sea water @ 17 Celsius)\n
            LBP, B, Cw, Lsc,\n
            Tlc ->  <float> Loading Condition Draught, Depth\n

        ---------+----------------------------------------------------------------------------------------------------------
        """
        return self.fxL, self.fps, self.fb, self.ft, self.rho, self.LBP, self.B, self.Cw, self.Lsc, self.Tlc, self.D

    def Combination_Factors(self):

        # C = ['Cwv','Cqw','Cwh','Cwt','Cxs','Cxp','Cxg','Cys','Cyr','Cyg','Czh','Czr','Czp']
        HSM_1 = [-1, -self.fps, 0, 0, 0.3 - 0.2 * self.ft, -0.7, 0.6, 0, 0, 0, 0.5 * self.ft - 0.15, 0, 0.7]
        HSA_1 = [-0.7, -0.6 * self.flp, 0, 0, 0.2, -0.4 * (self.ft + 1), 0.4 * (self.ft + 1), 0, 0, 0,
                 0.4 * self.ft - 0.1, 0, -0.4 * (self.ft + 1)]
        FSM_1 = [-0.4 * self.ft - 0.6, -self.fps, 0, 0, 0.2 - 0.4 * self.ft, 0.15, -0.2, 0, 0, 0, 0, 0, 0.15]
        BSR_1P = [0.1 - 0.2 * self.ft, (0.1 - 0.2 * self.ft) * self.flp, 1.2 * 1.1 * self.ft, 0, 0, 0, 0,
                  0.2 - 0.2 * self.ft, 1, -1, 0.7 - 0.4 * self.ft, 1, 0]
        BSP_1P = [0.3 - 0.8 * self.ft, (0.3 - 0.8 * self.ft) * self.flp, 0.7 - 0.7 * self.ft, 0, 0, 0.1 - 0.3 * self.ft,
                  0.3 * self.ft - 0.1, -0.9, 0.3, -0.2, 1, 0.3, 0.1 - 0.3 * self.ft]
        OSA_1P = [0.75 - 0.5 * self.ft, (0.6 - 0.4 * self.ft) * self.flp, .55 + 0.2 * self.ft, -self.flp_osa,
                  0.1 * self.ft - 0.45, 1, -1, -0.2 - 0.1 * self.ft, 0.3 - 0.2 * self.ft, 0.1 * self.ft - 0.2,
                  -0.2 * self.ft, 0.3 - 0.2 * self.ft, 1]
        OST_1P = [-0.3 - 0.2 * self.ft, (-.35 - .2 * self.ft) * self.flp, -.9, -self.flp_ost, 0.1 * self.ft - 0.15,
                  0.7 - 0.3 * self.ft, 0.2 * self.ft - 0.45, 0, 0.4 * self.ft - 0.25, 0.1 - 0.2 * self.ft,
                  0.2 * self.ft - 0.05, 0.4 * self.ft - 0.25, 0.7 - 0.3 * self.ft]

        MAP = {"HSM": HSM_1, "HSA": HSA_1, "FSM": FSM_1, "BSR": BSR_1P, "BSP": BSP_1P, "OSA": OSA_1P, "OST": OST_1P}

        try:
            RES = MAP[self.cond[:3]]
            if "_2" in self.cond:
                RES = [-1 * i for i in RES]
            return RES
        except KeyError:
            Logger.error(
                f"PhysicsData/Combination_Factors: {self.cond} is not a valid Dynamic Condition abbreviation.",
                die=False
            )
            Logger.error("Invalid condition to study. Enter an appropriate Condition out of :", die=False)
            [Logger.error(f"{i}", die=False) for i in self.fbeta]
            Logger.error(
                "Currently supported conditions are : HSM and BSP. "
                "The other conditions will result in invalid results",
                die=False
            )
            Logger.error("The Program Terminates...")

    def accel_eval(self, point):
        R = min((self.D / 4 + self.Tlc / 2, self.D / 2))
        x, y, z = point

        Logger.debug(
            f"Point [x,y,z] : {point}",
            f"'Cxs', {self.Cxs}, Cxp, {self.Cxp}, Cxg, {self.Cxg}, Cys, {self.Cys}, Cyr, {self.Cyr}, Cyg,"
            f" {self.Cyg}, Czh, {self.Czh}, Czr, {self.Czr}, Czp, {self.Czp}"
        )
        ax = -self.Cxg * G * math.sin(d2r(self.phi)) + self.Cxs * self.a_surge + self.Cxp * self.a_pitch * (z - R)
        ay = self.Cyg * G * math.sin(d2r(self.theta)) + self.Cys * self.a_sway - self.Cyr * self.a_roll * (z - R)
        az = self.Czh * self.a_heave + self.Czr * self.a_roll * y - self.Czp * self.a_pitch * (x - 0.45 * self.Lsc)

        return ax, ay, az

    def wave_pressure_functions(self):
        functions = {
            "HSM": hsm_wave_pressure,
            "BSP": bsp_wave_pressure
        }

        try:
            if ("-1P" in self.cond) or ("-2P" in self.cond):
                self.wave_pressure = functions[self.cond[:-3]]
            else:
                self.wave_pressure = functions[self.cond[:-2]]
        except KeyError as e:
            Logger.error(f"(physics.py) PhysicsData/wave_pressure_functions: '{self.cond[:-2]}' is not yet supported. "
                         f"Program terminates to avoid unpredictable behavior...", rethrow=e)

    def moments_eval(self):
        """
        IACS, CSR Part 1 Chapter 4 Section 4
        """
        fnl_h = 1.0  # strength assessment Hogging
        fnl_s = 0.58 * (self.Cb + 0.7) / self.Cb  # strength assessment Sagging
        fm_ = {
            0.0: 0.0,
            0.4: 1.0,
            0.6: 1.0,
            1.0: 0.0
        }
        fqpos_ = {
            0.0: 0.0,
            0.2: 0.92 * fnl_h,
            0.3: 0.92 * fnl_h,
            0.4: 0.7,
            0.6: 0.7,
            0.7: 1.0 * fnl_s,
            0.85: 1.0 * fnl_s,
            1.0: 0.0
        }
        fqneg_ = {
            0.0: 0.0,
            0.2: 0.92 * fnl_s,
            0.3: 0.92 * fnl_s,
            0.4: 0.7,
            0.6: 0.7,
            0.7: 1.0 * fnl_h,
            0.85: 1.0 * fnl_h,
            1.0: 0.0
        }
        fsw_ = {
            0.0: 0.0,
            0.1: 0.15,
            0.3: 1.0,
            0.7: 1.0,
            0.9: 0.15,
            1.0: 0.0
        }

        # Vertical Moment Calculation
        Mw_h = lambda x: 0.19 * fnl_h * x * self.fps * self.Cw * self.Lsc ** 2 * self.B * self.Cb
        Mw_s = lambda x: -0.19 * fnl_s * x * self.fps * self.Cw * self.Lsc ** 2 * self.B * self.Cb
        # Shear Forces Calculation
        Qpos = lambda x: 0.52 * x * self.fps * self.Cw * self.Lsc * self.B * self.Cb
        Qneg = lambda x: -0.52 * x * self.fps * self.Cw * self.Lsc * self.B * self.Cb

        fm = lin_int_dict(fm_, self.fxL)
        fm_mid = lin_int_dict(fm_, 0.5)
        fqpos = lin_int_dict(fqpos_, self.fxL)
        fqneg = lin_int_dict(fqneg_, self.fxL)
        fsw = lin_int_dict(fsw_, self.fxL)

        if self.Cwv >= 0:
            Mwv_lc = self.fb * self.Cwv * Mw_h(fm)
            Mws = fsw * ((0.171 * self.Cw * self.Lsc ** 2 * self.B * (self.Cb + 0.7)) - Mw_h(fm_mid))
        else:
            Mwv_lc = self.fb * self.Cwv * abs(Mw_s(fm))
            Mws = -0.85 * fsw * ((0.171 * self.Cw * self.Lsc ** 2 * self.B * (self.Cb + 0.7)) + Mw_s(fm_mid))

        if self.Cqw >= 0:
            Qwv_lc = self.fb * self.Cqw * Qpos(fqpos)
        else:
            Qwv_lc = self.fb * self.Cqw * abs(Qneg(fqneg))
        # Horizontal Moment Calculation
        Mwh = 0.9 * self.fps * fm * (0.31 + self.Lsc / 2800) * self.Cw * self.Lsc ** 2 * self.Tlc * self.Cb

        return Mwv_lc, Qwv_lc, self.Cwh * Mwh, Mws
