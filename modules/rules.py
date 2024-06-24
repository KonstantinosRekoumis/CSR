# #############################
# CSR Rules and Regulations for Dry Cargo
# #############################

# Materials Constant Array see. CSR ... to be filled
import math
from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.baseclass.block import Block, SpaceType
from modules.baseclass.ship import Ship
from modules.io.datalogger import DataLogger
from modules.physics.data import Data
from modules.utils.constants import MATERIALS
from modules.utils.logger import Logger


# page 378 the application table
# ------------------- Thickness Calculation Functions --------------------------
def minimum_plate_net_thickness(plate: StiffPlate, l2: float, debug=False):
    """
    -----------------------------------------
    IACS Part 1 Chapter 6, Section 3.1
    Table 1
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.
    """
    _CHECK_ = {
        "Shell": {
            "Keel": (7.5 + 0.03 * l2) * 1e-3,
            "Else": (5.5 + 0.03 * l2) * 1e-3
        },
        "Hopper/Wing-BC": math.sqrt(l2) * 0.7 * 1e-3,
        "Deck": (4.5 + 0.02 * l2) * 1e-3,
        "InnerBottom": (5.5 + 0.03 * l2) * 1e-3,
        "OtherPlates": (4.5 + 0.01 * l2) * 1e-3
    }

    if debug:
        out = "Empirical thicknesses : "
        for i in _CHECK_:
            if i != "Shell":
                out += f"{i} -> {_CHECK_[i] * 1e3} mm\n"
                continue

            keel = _CHECK_[i]["Keel"]
            else_ = _CHECK_[i]["Else"]
            out += f"Keel -> {keel * 1e3} mm\n"
            out += f"Else -> {else_ * 1e3} mm\n"

        Logger.debug(out)

    match plate.tag:
        case 0 | 4:
            # keel plate
            if plate.plate.start[0] == 0:
                if plate.plate.net_thickness_empi < _CHECK_["Shell"]["Keel"]:
                    Logger.debug((f"Stiffened plate's : {plate} net plate  thickness {plate.plate.net_thickness_empi} "
                                  f"was lower than", _CHECK_["Shell"]["Keel"], ". Thus it was changed to the appropriate value"))
                    plate.plate.net_thickness_empi = _CHECK_["Shell"]["Keel"]
                    return

                Logger.debug((f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                              f"was greater than", _CHECK_["Shell"]["Keel"]))
                return

            if plate.plate.net_thickness_empi < _CHECK_["Shell"]["Else"]:
                Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                             f"was lower than", _CHECK_["Shell"]["Else"], ". Thus it was changed to the appropriate value")
                plate.plate.net_thickness_empi = _CHECK_["Shell"]["Else"]
                return

            Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                         f"was greater than", _CHECK_["Shell"]["Else"])

        case 1:
            if plate.plate.net_thickness_empi < _CHECK_["InnerBottom"]:
                Logger.debug(f"Stiffened plate's : {plate} net plate  thickness {plate.plate.net_thickness_empi} "
                              f"was lower than", _CHECK_["InnerBottom"], ". Thus it was changed to the appropriate value")
                plate.plate.net_thickness_empi = _CHECK_["InnerBottom"]
                return

            Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                          f"was greater than", _CHECK_["InnerBottom"])

        # and ship.type == 'BulkCarrier': (implement later)
        case 2 | 3:
            if plate.plate.net_thickness_empi < _CHECK_["Hopper/Wing-BC"]:
                Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                             f"was lower than", _CHECK_["Hopper/Wing-BC"], ". Thus it was changed to the appropriate value")
                plate.plate.net_thickness_empi = _CHECK_["Hopper/Wing-BC"]
                return

            Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                         f"was greater than", _CHECK_["OtherPlates"])

        case 5:
            if plate.plate.net_thickness_empi < _CHECK_['Deck']:
                Logger.debug(f"Stiffened plate's : {plate} net plate thickness {plate.plate.net_thickness_empi} "
                              f"was lower than", _CHECK_["Deck"], ". Thus it was changed to the appropriate value")
                plate.plate.net_thickness_empi = _CHECK_['Deck']
                return

            Logger.debug(f"Stiffened plate's : {plate} net plate  thickness {plate.plate.net_thickness_empi} "
                         f"was greater than", _CHECK_["Deck"])

        case _:
            Logger.error(f"(rules.py) minimum_plate_net_thickness: Plate {plate}. You are not supposed to enter here.")


def minimum_stiff_net_thickness(plate: StiffPlate, l2: float):
    """
    -----------------------------------------
    IACS Part 1 Chapter 6, Section 3.2
    Table 2
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.\n
    To be called explicitly after checking the respective stiffened plate's plate.
    """
    _CHECK_ = {
        "Longs": {
            "Watertight": (3.5 + 0.015 * l2) * 1e-3,
            "Else": (3.0 + 0.015 * l2) * 1e-3
        }
    }

    # must calculate first its pressure thickness
    sup = 2.0 * plate.plate.net_thickness
    base = max(_CHECK_["Longs"]["Watertight"], 0.4 * plate.plate.net_thickness)
    update = False
    if plate.stiffeners[0].type == 'fb' or plate.stiffeners[0].type in ('g', 'tb'):
        stiff = plate.stiffeners[0]
        if (stiff.plates[0].net_thickness_empi < base) and (stiff.plates[0].net_thickness_empi < sup):
            # For the time being every Longitudinal is on a watertight plate
            Logger.debug((f"Stiffened plate's : {plate} Stiffener Web plate thickness was lower than", base,
                          ". Thus it was changed to the appropriate value"))
            stiff.plates[0].net_thickness_empi = base
            update = True
        elif (stiff.plates[0].net_thickness_empi > base) and (stiff.plates[
                                                                  0].net_thickness_empi > sup):
            # For the time being every Longitudinal is on a watertight plate
            Logger.debug((f"Stiffened plate's : {plate} Stiffener Web plate thickness was greater than", sup,
                          ". Thus it was changed to the appropriate value"))
            stiff.plates[0].net_thickness_empi = sup
            update = True
        else:
            Logger.debug(f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits')
        if (stiff.plates[1].net_thickness_empi < base) and (stiff.plates[1].net_thickness_empi < sup):
            # For the time being every Longitudinal is on a watertight plate
            Logger.debug((f"Stiffened plate's : {plate} Stiffener  Flange plate thickness was lower than", base,
                          ". Thus it was changed to the appropriate value"))
            stiff.plates[1].net_thickness_empi = base
            update = True
        elif (stiff.plates[1].net_thickness_empi > base) and (stiff.plates[1].net_thickness_empi > sup):
            # For the time being every Longitudinal is on a watertight plate
            Logger.debug((f"Stiffened plate's : {plate} Stiffener  Flange plate thickness was greater than", sup,
                          ". Thus it was changed to the appropriate value"))
            stiff.plates[1].net_thickness_empi = sup
            update = True
        else:
            Logger.debug(f"Stiffened plate's : {plate}  Stiffener Flange plate thickness was within limits")

    else:
        Logger.error(f"(rules.py) minimum_stiff_net_thickness: Plate {plate}. You are not supposed to enter here.")
    if update:
        if plate.stiffeners[0].type == 'fb':
            for stiff in plate.stiffeners[1:]:
                stiff.plates[0].net_thickness_empi = plate.stiffeners[0].plates[0].net_thickness_empi
        elif plate.stiffeners[0].type in ('g', 'tb'):
            for stiff in plate.stiffeners[1:]:
                stiff.plates[0].net_thickness_empi = plate.stiffeners[0].plates[0].net_thickness_empi
                stiff.plates[1].net_thickness_empi = plate.stiffeners[0].plates[1].net_thickness_empi


def plating_net_thickness_calculation(ship: Ship, plate: StiffPlate, case: Data, dynamic=False, debug=False):
    """
    IACS Part 1 Chapter 6, Section 4
    """

    # application point to be on the stiffeners
    x = {
        0: 1.0,  # "Shell"
        1: 0.7,  # 'InnerBottom'
        2: 0.7,  # 'Hopper'
        3: 1.0,  # 'Wing'
        4: 1.0,  # 'Bilge'
        5: 1.0  # 'WeatherDeck'
    }
    ap = 1.2 - plate.spacing ** 2 / 2.1 / plate.psm_spacing
    try:
        reh, rem, teh = MATERIALS[plate.plate.material]
    except KeyError:
        Logger.warning(f"(rules.py) plating_thickness_calculation: "
                       f"Stiffened plate's plate {plate} has material {plate.plate.material} "
                       f"that is not documented in this program. "
                       f"Either consider changing it or modify constants.py MATERIALS dict. "
                       f"Defaulting to A grade steel (Rm = 255)...")

    def ca(point):
        ca_ = min(1.05 - 0.5 * abs(case.sigma(*point)) / reh, 0.95)
        if dynamic:
            ca_ = min(0.9 - 0.5 * abs(case.sigma(*point)) / reh, 0.8)

        if ca_ < 0:
            Logger.warning(f"(rules.py) plating_thickness_calculation/Ca: Ca coefficient has been found negative! "
                           f"This is due to having an extremely low Area Moment of Inertia.\n "
                           f"I assume that this is the first design circle and therefore Ca_max will be used!")
            if dynamic:
                return 0.8
            return 0.95
        return ca_

    t = lambda point, p: 0.0158 * ap * plate.spacing * math.sqrt(abs(p) / x[plate.tag] / ca(point) / reh)
    max_t = 0

    try:
        Logger.debug(f'net_plating plate:{plate}')
        for i, data in enumerate(plate.Pressure[case.cond]):
            point = (data[0], data[1])
            p = data[-1]
            Logger.debug(f"Press: {p}, "
                         f"Point: {point}, "
                         f"sigma {abs(case.sigma(*point))}, "
                         f"Ca {ca(point)}")
            t_temp = t(point, p)
            Logger.debug(f"t_temp:{t_temp}")
            max_t = t_temp if max_t < t_temp else max_t
        Logger.debug(f", max_t:{max_t}")
    except KeyError:
        Logger.warning(f"(rules.py) plating_thickness_calculation: The {case.cond} "
                       f"condition has not been calculated for  plate {plate}. "
                       f"Checking only the empirical thickness value...")
        minimum_plate_net_thickness(plate, l2=min(300, case.Lsc), debug=debug)
        return None

    # Special Cases
    if (plate.tag == 0) and ((ship.Tmin < plate.plate.start[1] < 1.25 * ship.Tsc)
                             or (ship.Tmin < plate.plate.end[1] < 1.25 * ship.Tsc)):
        t = 26 * (plate.spacing + 0.7) * (ship.B * ship.Tsc / reh ** 2) ** 0.25 * 1e-3  # m
        Logger.debug(f"(rules.py) plating_thickness_calculation: Plate {plate} "
                     f"Contact Fender Zone special t {t * 1e3} while local scantlings t {max_t * 1e3} [mm]")
    elif plate.tag == 4:
        p = plate.Pressure[case.cond][0][-1]
        r = abs(plate.plate.start[1] - plate.plate.end[1]) + 0.5 * (plate.s_pad + plate.e_pad)
        t = 6.45 * (p * plate.psm_spacing * 1e3) ** 0.4 * (r * 1e3) ** 0.6 * 1e-7  # m
        Logger.debug(f"(rules.py) plating_thickness_calculation: Plate {plate} "
                     f"Bilge Zone special t {t * 1e3} while local scantlings t {max_t * 1e3} [mm]")
    else:
        t = 0

    if plate.plate.net_thickness_calc < max(t, max_t):
        plate.plate.net_thickness_calc = max(t, max_t)

    minimum_plate_net_thickness(plate, l2=min(300, case.Lsc), debug=debug)  # need to check what L2 is
    plate.update()


def stiffener_plating_net_thickness_calculation(plate: StiffPlate, case: Data, dynamic=False):
    """
    IACS Part 1 Chapter 6, Section 4
    """
    try:
        reh, rem, teh = MATERIALS[plate.stiffeners[0].plates[0].material]
    except KeyError:
        Logger.warning(f"(rules.py) plating_thickness_calculation: "
                       f"Stiffened plate's plate {plate} has material {plate.plate.material} that is not documented "
                       f"in this program. Either consider changing it or modify constants.py MATERIALS dict. "
                       f"Defaulting to A grade steel (Rm = 255)...")
    x = {
        0: 1.0,  # "Shell"
        1: 0.9,  # 'InnerBottom'
        2: 0.9,  # 'Hopper'
        3: 1.0,  # 'Wing'
        4: 1.0,  # 'Bilge'
        5: 1.0  # 'WeatherDeck'
    }
    ct_ = {
        "AC-S": 0.75,
        "AC-SD": 0.90
    }
    ct = ct_["AC-S"] if dynamic else ct_["AC-SD"]

    def cs(sigma):
        if dynamic:  # AC-S
            if sigma >= 0:
                return 0.75
            return 0.85 - abs(sigma) / reh
        # AC-SD
        if sigma >= 0:
            return 0.9
        return 1.0 - abs(sigma) / reh

    # hardcoded that phiw = 90 deg This is a critical assumption
    dshr = (plate.plate.length + plate.stiffeners[0].plates[0].net_thickness + 0.5 * plate.plate.cor_thickness - 0.5 *
            plate.stiffeners[0].plates[0].net_thickness) * 1.0

    fshr = 0.7  # lower end of vertical stiffeners is the minimum worst condition
    fbdg = 12  # horizontal stiffeners

    lbdg = plate.psm_spacing  # worst case scenario don't know the stiffener span
    lshr = plate.psm_spacing - plate.spacing / 2  # worst case scenario don't know the stiffener span
    tw = lambda p: (fshr * abs(p) * plate.spacing * lshr) / (dshr * x[plate.tag] * ct * teh) * 1e-3
    z = lambda p, point: (abs(p) * plate.spacing * 1e3 * lbdg ** 2) / (
            fbdg * x[plate.tag] * cs(case.sigma(*point)) * reh) * 1e-6

    max_t = 0
    max_z = 0
    p = 0
    for i, stiff in enumerate(plate.stiffeners):
        try:
            p = plate.local_P(case.cond, stiff.plates[0].start)
        except KeyError:
            Logger.warning(f"(rules.py) stiffener_plating_thickness_calculation: "
                           f"The {case.cond} condition has not been calculated for this plate. "
                           f"Checking only the empirical thickness value...")
            break
        t_tmp = tw(p)
        if max_t < t_tmp:
            max_t = t_tmp
    if plate.stiffeners[0].plates[0].net_thickness_calc < max_t:
        for stiff in plate.stiffeners:
            if len(stiff.plates) > 1:
                for st_pl in stiff.plates:
                    st_pl.net_thickness_calc = max_t
            stiff.plates[0].net_thickness_calc = max_t

    minimum_stiff_net_thickness(plate, min(300, case.Lsc))
    plate.update()
    for i, stiff in enumerate(plate.stiffeners):
        z_tmp = z(p, stiff.plates[0].start)
        if max_z < z_tmp:
            max_z = z_tmp
    z_local = plate.stiffeners[0].calc_Z()
    if max_z > plate.stiffeners[0].Z_rule:
        for i in plate.stiffeners:
            i.Z_rule = max_z

    if max_z > z_local:
        Logger.warning(f"(rules.py) stiffener_plating_net_thickness_calculation: "
                       f"Plate {plate} Z is less than Z calculated by regulations ({z_local * 1e6} < {max_z * 1e6})")
        Logger.warning(f"Consider fixing it manually, as an automatic solution is not currently possible.")


def buckling_evaluator(ship: Ship):
    """
    IACS PART 1 CHAPTER 8 SECTION 2
    Slenderness requirements 
    """
    cwcf = {
        "fb": (22,),
        "bb": (45,),
        "tb": (75, 12),
        "g": (75, 12)
    }

    # longitudinals
    c = 1.43
    Logger.debug("Buckling check")

    for st_plate in ship.stiff_plates:
        Logger.debug(st_plate)

        if len(st_plate.stiffeners) <= 0 or st_plate.tag in (4, 6):
            continue

        reh = min(MATERIALS[st_plate.plate.material][0], MATERIALS[st_plate.stiffeners[0].material][0])
        n = len(st_plate.stiffeners)
        aeff = n * st_plate.stiffeners[0].area + st_plate.plate.thickness * st_plate.b_eff  # m^2
        ist = n * c * st_plate.psm_spacing ** 2 * aeff * reh / 235 * 1e-4  # m^4

        # thickness check
        tp = st_plate.b_eff / 100 * math.sqrt(reh / 235)

        Logger.debug("b_eff: ", st_plate.b_eff)
        Logger.debug("tp: ", tp)

        if st_plate.plate.net_thickness_calc < tp:
            if st_plate.plate.net_thickness < tp:
                Logger.warning(f"(rules.py) buckling_evaluator: "
                               f"Available tp: {st_plate.plate.net_thickness * 1e3} mm is less than minimum "
                               f"tp: {tp * 1e3} mm by the rules for plate {st_plate} ")
            st_plate.plate.net_thickness_calc = tp
        tw = st_plate.stiffeners[0].plates[0].length / cwcf[st_plate.stiffeners[0].type][0] * math.sqrt(reh / 235)

        Logger.debug("tw: ", tw)

        if st_plate.stiffeners[0].plates[0].net_thickness_buck < tw:
            if st_plate.stiffeners[0].plates[0].net_thickness < tw:
                Logger.warning(f"(rules.py) buckling_evaluator: "
                               f"Available tw: {st_plate.stiffeners[0].plates[0].net_thickness * 1e3} mm is less than minimum "
                               f"tw: {tw * 1e3} mm by the rules for plate {st_plate} ")
            st_plate.stiffeners[0].plates[0].net_thickness_buck = tw

        if st_plate.stiffeners[0].type in ('tb', 'g'):
            tf = (math.sqrt((st_plate.stiffeners[0].plates[1].end[0] - st_plate.stiffeners[0].plates[0].end[0]) ** 2
                            + (st_plate.stiffeners[0].plates[1].end[1] - st_plate.stiffeners[0].plates[0].end[1]) ** 2)
                  / cwcf[st_plate.stiffeners[0].type][1] * math.sqrt(reh / 235))

            Logger.debug("tf: ", tf)

            if st_plate.stiffeners[0].plates[1].net_thickness_buck < tf:
                if st_plate.stiffeners[0].plates[1].net_thickness < tf:
                    Logger.warning(f"(rules.py) buckling_evaluator: "
                                   f"Available tf: {st_plate.stiffeners[0].plates[1].net_thickness * 1e3} "
                                   f"mm is less than minimum "
                                   f"tf: {tf * 1e3} mm by the rules for plate {st_plate} ")
                st_plate.stiffeners[0].plates[1].net_thickness_buck = tf
        # Area Moment check
        st_plate.update()

        Logger.debug("Ist: ", ist, "Ieff: ", st_plate.Ixx_c)

        if st_plate.Ixx_c < ist:
            Logger.warning(f"(rules.py) buckling_evaluator: "
                           f"Available Ieff: {st_plate.Ixx_c} is less than minimum "
                           f"Ieff: {ist} by the rules for plate {st_plate}")
        ship.update()


# ----------------  Loading cases manager function  ----------------------------
def loading_cases_eval(ship: Ship, case: Data, condition: dict, logger: DataLogger):
    """
    condition = {
        'Dynamics':'SD',
        'max value': 'DC,WB',
        'skip value':'LC'
    }
    """

    def maximum_p(p):
        max_p = 0
        index = 0

        for i, P_ in enumerate(p):
            local_max = max(P_, key=lambda k: abs(k[-1]))
            if max_p < local_max[-1]:  # Pressure position
                max_p = local_max[-1]
                index = i
        return index

    for plate in ship.stiff_plates:
        # skip calculation for null plates and girders
        if plate.null or plate.tag == 6:
            continue

        blocks = []
        max_eval = False
        for block in ship.blocks:

            plate_id_is_in_block_ids = plate.id in block.list_plates_id
            inverse_plate_is_in_block_ids = -plate.id in block.list_plates_id
            if not (plate_id_is_in_block_ids or inverse_plate_is_in_block_ids):
                continue
            if block.space_type not in condition['skip value']:
                blocks.append(block)
                continue
            # use a zero pressure pseudo block as the plate is well-defined
            #  and raising an exception is unwanted behavior
            zero = Block("zero", False, SpaceType.VoidSpace, [plate.id])
            zero.get_coords([plate, ])
            zero.Pressure[case.cond] = [0 for _ in zero.pressure_coords]
            blocks.append(zero)

        if len(blocks) > 2 or len(blocks) == 0:
            Logger.error(
                f"(rules.py) Loading_cases: Detected a plate: {plate} which is contained in multiple blocks. "
                f"A stiffened plate can be boundary of only 2 Blocks at most at a time!")
            Logger.error(f"Involved Blocks:\n {blocks}")
            quit()

        for block in blocks:
            max_eval = block.space_type in condition['max value'] and not max_eval
            if max_eval:
                break

        if max_eval:
            p = []
            for block in blocks:
                # force the singular evaluation of each pressure distribution
                p.append(plate_pressure_assigner([block], plate, case, condition['Dynamics']))
            p_max = maximum_p(p)
            plate.Pressure[case.cond] = p[p_max]
        else:
            # let the function handle the proper aggregation
            plate.Pressure[case.cond]= plate_pressure_assigner(blocks, plate, case, condition['Dynamics'])
        logger.update_stiff_plate(plate)  # save pressure maximum pressure data


def ship_scantlings(ship: Ship):
    in50 = 2.7 * ship.Cw * ship.Lsc ** 3 * ship.B * (ship.Cb + 0.7) * 1e-8
    # k = 1.0 Grade A steel(not a good idea, pretty retarded)
    zrn50 = 0.9 * ship.kappa * ship.Cw * ship.Lsc ** 2 * ship.B * (ship.Cb + 0.7) * 1e-6
    zn50k_ship = ship.n50_Ixx / ship.yo
    zn50d_ship = ship.n50_Ixx / abs(ship.yo - ship.D)

    # FIXME this is borderline beyond saving, we need better checks or at least a better format for them
    Logger.debug(f"(rules.py) ship_scantlings: The ship's neutral axis is at {ship.yo:0.5g} meters from Keel")
    if ship.n50_Ixx < in50:
        Logger.warning(
            f"(rules.py) ship_scantlings: "
            f"The Area Inertia Moment of the ship In50 : {ship.n50_Ixx:0.5g} is less than "
            f"In50: {in50:0.5g} calculated by the rules")
    else:
        Logger.success(
            f"(rules.py) ship_scantlings: "
            f"The Area Inertia Moment of the ship In50 : {ship.n50_Ixx:0.5g} is adequate compared to "
            f"In50: {in50:0.5g} calculated by the rules")
    if zn50k_ship < zrn50:
        Logger.warning(
            f"(rules.py) ship_scantlings: "
            f"The Section Modulus at Keel of the ship Zn50,keel : {zn50k_ship:0.5g} is less than "
            f"Zrn50: {zrn50:0.5g} calculated by the rules")
    else:
        Logger.success(
            f"(rules.py) ship_scantlings: "
            f"The Section Modulus at Keel of the ship Zn50,keel : {zn50k_ship:0.5g} is adequate compared to "
            f"Zrn50: {zrn50:0.5g} calculated by the rules")
    if zn50d_ship < zrn50:
        Logger.warning(
            f"(rules.py) ship_scantlings: "
            f"The Section Modulus at Depth of the ship Zn50,Depth : {zn50d_ship:0.5g} is less than "
            f"Zrn50: {zrn50:0.5g} calculated by the rules")
    else:
        Logger.success(
            f"(rules.py) ship_scantlings: "
            f"The Section Modulus at Depth of the ship Zn50,Depth : {zn50d_ship:0.5g} is adequate compared to "
            f"Zrn50: {zrn50:0.5g} calculated by the rules")


def net_scantling(ship: Ship, case: Data, dynamics: str, debug=True):
    _Dynamic = False
    if "d" in dynamics or "D" in dynamics:
        _Dynamic = True

    for stiff_plate in ship.stiff_plates:
        # skip calculation for null plates and girders
        if stiff_plate.null or stiff_plate.tag == 6:
            continue
        Logger.debug(f"(rules.py) net_scantling: Evaluating plate's :{stiff_plate} PLATES NET SCANTLING")
        plating_net_thickness_calculation(ship, stiff_plate, case, dynamic=_Dynamic, debug=debug)
        Logger.debug(f"(rules.py) net_scantling: Evaluated plate's :{stiff_plate} PLATES NET SCANTLING")
    ship.update()

    for stiff_plate in ship.stiff_plates:
        # skip calculation for null plates and girders
        if stiff_plate.null or stiff_plate.tag == 6:
            continue
        Logger.debug(f"(rules.py) net_scantling: Evaluating plate's {stiff_plate} STIFFENERS NET SCANTLING")
        # Bilge plate and other loose plates
        if len(stiff_plate.stiffeners) != 0:
            stiffener_plating_net_thickness_calculation(stiff_plate, case, dynamic=_Dynamic)
    ship.update()


def corrosion_addition(stiff_plate: StiffPlate, blocks: list[Block], tmin, tmax):
    # CSR Chapter 1, Section 3
    corr = {
        "WBT": {
            "FacePlate": {
                "=< 3,tank_top": 2.0,
                "else": 1.5},
            "OtherMembers": {
                "=< 3,tank_top": 2.0,
                "else": 1.5}
        },
        "CHP": {
            "UpperPart": 1.8,
            "Hopper/InBot": 3.7
        },
        "X2A": {
            "WeatherDeck": 1.7,
            "Other": 1.0
        },
        "X2SW": {
            "Wet/Dried": 1.5,
            "Wet": 1.0
        },
        "Misc": {
            "FO/FW/LO/VS": 0.7,
            "DrySpace": 0.5
        }

    }
    # Grab tags
    tags = []
    for i in blocks:
        if stiff_plate.id in i.list_plates_id or -stiff_plate.id in i.list_plates_id:
            tags.append(i.space_type)
    plate_t_corr = {
        "in": 0,
        "out": 0,
    }
    if len(tags) == 0:
        Logger.warning(
            (f"(rules.py) corrosion_addition:/ Stiffened plate's {stiff_plate} locality data are not present."
             "Resetting to the Hopper case for both sides"))
        plate_t_corr["in"] = corr["CHP"]["Hopper/InBot"]
        plate_t_corr["out"] = corr["CHP"]["Hopper/InBot"]
        return plate_t_corr

    if stiff_plate.tag in (0, 4):  # Shell plates
        y = max(stiff_plate.plate.start[1], stiff_plate.plate.end[1])
        if y <= tmin:
            plate_t_corr["out"] = corr["X2SW"]["Wet"]
        elif tmin < y < tmax:
            plate_t_corr["out"] = corr["X2SW"]["Wet/Dried"]
        elif y > tmax:
            plate_t_corr["out"] = corr["X2A"]["WeatherDeck"]  # Is it tho ?

        # FIXME remove duplicate with line 686
        t_in = 0
        for i in tags:
            if i is SpaceType.WaterBallast:
                if t_in < corr["WBT"]["FacePlate"]["=< 3,tank_top"]:
                    t_in = corr["WBT"]["FacePlate"]["=< 3,tank_top"]
            elif i is SpaceType.DryCargo:
                if t_in < corr["CHP"]["UpperPart"]:
                    t_in = corr["CHP"]["UpperPart"]
            elif i in [SpaceType.OilTank, SpaceType.FreshWater]:
                if t_in < corr["Misc"]["FO/FW/LO/VS"]:
                    t_in = corr["Misc"]["FO/FW/LO/VS"]
            elif i is SpaceType.VoidSpace:
                if t_in < corr["Misc"]["DrySpace"]:
                    t_in = corr["Misc"]["DrySpace"]

        plate_t_corr['in'] = t_in

    elif stiff_plate.tag in (1, 2, 3):  # Inner Bottom, Hopper, Wing
        t = [0, 0]
        ind = 0
        c = 0
        if len(tags) == 1:
            Logger.warning(
                (f'(rules.py) corrosion_addition:/ Stiffened plate\'s {stiff_plate} locality data are inadequate.'
                 'Using the data of the one side for both sides ...'))
            tags.append(tags[0])

        # not the best way but oh well
        while c <= 1:
            for i, tag in enumerate(tags):
                if tag is SpaceType.WaterBallast:
                    if t[c] < corr['WBT']['FacePlate']['=< 3,tank_top']:
                        t[c] = corr['WBT']['FacePlate']['=< 3,tank_top']
                        ind = i
                elif tag is SpaceType.DryCargo:
                    if t[c] < corr["CHP"]["Hopper/InBot"]:
                        t[c] = corr["CHP"]["Hopper/InBot"]
                        ind = i
                elif tag in [SpaceType.OilTank, SpaceType.FreshWater]:
                    if t[c] < corr["Misc"]["FO/FW/LO/VS"]:
                        t[c] = corr["Misc"]["FO/FW/LO/VS"]
                        ind = i
                elif tag is SpaceType.VoidSpace:
                    if t[c] < corr["Misc"]["DrySpace"]:
                        t[c] = corr["Misc"]["DrySpace"]
                        ind = i
            tags.pop(ind)
            c += 1
        # No respect for the actual geometry but I 'ld rather over-engineer stiffener scantlings
        plate_t_corr['in'] = max(t)
        plate_t_corr['out'] = min(t)
    elif stiff_plate.tag == 5:  # Weather Deck
        plate_t_corr['out'] = corr["X2A"]["WeatherDeck"]

        t_in = 0
        for i in tags:
            if i is SpaceType.WaterBallast:
                if t_in < corr["WBT"]["FacePlate"]["=< 3,tank_top"]:
                    t_in = corr["WBT"]["FacePlate"]["=< 3,tank_top"]
            elif i is SpaceType.DryCargo:
                if t_in < corr["CHP"]["UpperPart"]:
                    t_in = corr["CHP"]["UpperPart"]
            elif i in [SpaceType.OilTank, SpaceType.FreshWater]:
                if t_in < corr["Misc"]["FO/FW/LO/VS"]:
                    t_in = corr["Misc"]["FO/FW/LO/VS"]
            elif i is SpaceType.VoidSpace:
                if t_in < corr["Misc"]["DrySpace"]:
                    t_in = corr["Misc"]["DrySpace"]

        plate_t_corr['in'] = t_in

    return plate_t_corr


def corrosion_assign(ship: Ship, offload: bool):
    """
    Data input assumes gross thickness scantling.\n
    Input = True, offloads the corrosion addition to assign the net scantling
    Input = False, loads the corrosion addition to assign the new gross scantling
    """

    def round_to_p5(num):
        return math.ceil(num * 2) / 2

    if offload:
        for stiff_plate in ship.stiff_plates:
            # skip calculation for null plates and girders and girders
            if stiff_plate.null or stiff_plate.tag == 6:
                continue
            c_t = corrosion_addition(stiff_plate, ship.blocks, ship.Tmin, ship.Tsc)
            stiff_plate.plate.cor_thickness = (round_to_p5(c_t['in'] + c_t['out']) + 0.5) * 1e-3
            stiff_plate.plate.net_thickness = stiff_plate.plate.thickness - stiff_plate.plate.cor_thickness

            # maybe redundant but a good sanity check
            assert stiff_plate.plate.net_thickness > 0

            for stiffener in stiff_plate.stiffeners:
                for plate in stiffener.plates:
                    plate.cor_thickness = (round_to_p5(c_t['out'] + c_t['in']) + 0.5) * 1e-3
                    plate.net_thickness = plate.thickness - plate.cor_thickness
                    if plate.net_thickness < 0:
                        plate.net_thickness = 1e-3
        return

    for stiff_plate in ship.stiff_plates:
        # skip calculation for null plates and girders and girders
        if stiff_plate.null or stiff_plate.tag == 6:
            continue
        if stiff_plate.plate.cor_thickness < 0:
            Logger.error(f"(rules.py) corrosion_assign: "
                         f"Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!"
                         )
            quit()
        stiff_plate.plate.thickness = stiff_plate.plate.net_thickness + stiff_plate.plate.cor_thickness
        for stiffener in stiff_plate.stiffeners:
            for plate in stiffener.plates:
                if plate.cor_thickness < 0:
                    Logger.error(f"(rules.py) corrosion_assign: "
                                 f"Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!"
                                 )
                    quit()
                plate.thickness = plate.net_thickness + plate.cor_thickness


def plate_pressure_assigner(blocks: list[Block], plate: StiffPlate, case: Data, load: str):
    """
    ---------------------------------------------------------------------------
    Populate the pressure data of each plate\n
    Based on which plate is on top of whom (z = 0 @ keel, positives extend to the Main Deck )\n
    Transverse plates are not implemented yet.
    return_ parameter switches the data flow from immediate population of the Pressure Dictionary
     to return the Pressure Data in a variable
    ---------------------------------------------------------------------------
    """

    def mul(a, b):
        """
        Consider 2 vectors 2-D vectors
        """

        try:
            for i in (a, b):
                if len(i) != 2:
                    raise ValueError()
            return a[0] * b[0] + a[1] * b[1]
        except ValueError:
            Logger.error(f'(physics.py) block_to_plate_perCase/mul: Plate {plate} Vector {i} is not of proper type.')
            quit()

    def add_proj(a, b, proj_v, intermediate=False):
        """
        Input arguments are two Pressure data lists obtained from a block and a projection vector (the normals of a plate or a block)
        """
        P = []
        if len(a) != len(b):
            Logger.error(
                f'(physics.py) block_to_plate_perCase/add_proj: Plate {plate} Vector a has length {len(a)} while Vector b has length {len(b)} !')
        elif len(a) != len(proj_v):
            Logger.error(
                f'(physics.py) block_to_plate_perCase/add_proj: Plate {plate} Vector a has length {len(a)} while Projection Vector  has length {len(proj_v)} !')
        for i in range(len(a)):
            P0 = (a[i][2] * a[i][4], a[i][3] * a[i][4])  # (etax*P,etay*P)
            P1 = (b[i][2] * b[i][4], b[i][3] * b[i][4])  # (etax*P,etay*P)
            # Pressures are applied plate side!
            if not intermediate:
                P.append((a[i][0], a[i][1], mul(proj_v[i], (
                    P0[0] + P1[0],
                    P0[1] + P1[1]))))  # Vector Addition for the pressures and then projection on the plate
            else:
                P.append((a[i][0], a[i][1], proj_v[i][0], proj_v[i][1], mul(proj_v[i], (
                    P0[0] + P1[0],
                    P0[1] + P1[1]))))  # Vector Addition for the pressures and then projection on the plate
        return P

    P = []
    out_P = []
    if 'S' not in load or 'D' not in load:
        Logger.error(f"Load parameter is not of correct type. "
                     f"Expected 'S' or 'D' or 'S+D' etc. got {load}.")
    for i, block in enumerate(blocks):
        tmp = []
        if "D" in load:
            tmp.append(block.pressure_over_plate(plate, case.cond))
        if "S" in load:
            tmp.append(block.pressure_over_plate(plate, "STATIC"))
        if len(tmp) == 2:
            normals = [(i[2], i[3]) for i in tmp[0]]
            P.append(add_proj(tmp[0], tmp[1], normals, intermediate=True))
        elif len(tmp) == 1:
            P.append(tmp[0])

    if len(P) == 2:
        out_P = add_proj(P[0], P[1], [plate.plate.eta[0] for _ in P[0]])
    elif len(P) == 1:
        out_P = P[0]

    return out_P
