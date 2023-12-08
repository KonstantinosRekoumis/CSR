# #############################
# CSR Rules and Regulations for Dry Cargo
# #############################

# Materials Constant Array see. CSR ... to be filled
import math

import modules.classes as cls
import modules.physics as phzx
from modules.constants import MATERIALS
from modules.utilities import c_error, c_info, c_success, c_warn


# page 378 the application table
# ------------------- Thickness Calculation Functions --------------------------
def minimum_plate_net_thickness(plate: cls.StiffPlate, L2: float, Debug=False):
    """
    -----------------------------------------
    IACS Part 1 Chapter 6, Section 3.1
    Table 1
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.
    """
    _CHECK_ = {
        'Shell': {
            'Keel': (7.5 + 0.03 * L2) * 1e-3,
            'Else': (5.5 + 0.03 * L2) * 1e-3
        },
        'Hopper/Wing-BC': math.sqrt(L2) * 0.7 * 1e-3,
        'Deck': (4.5 + 0.02 * L2) * 1e-3,
        'InnerBottom': (5.5 + 0.03 * L2) * 1e-3,
        'OtherPlates': (4.5 + 0.01 * L2) * 1e-3
    }
    if Debug:
        out = "Empirical thicknesses : "
        for i in _CHECK_:
            if i == 'Shell':
                keel = _CHECK_[i]['Keel']
                else_ = _CHECK_[i]['Else']
                out += f'Keel -> {keel * 1e3} mm\n'
                out += f'Else -> {else_ * 1e3} mm\n'
            else:
                out += f'{i} -> {_CHECK_[i] * 1e3} mm\n'
        c_info(out)
    if plate.tag in (0, 4):
        if plate.plate.start[0] == 0:  # keel plate
            if plate.plate.net_thickness_empi < _CHECK_['Shell']['Keel']:
                if Debug: c_info((
                    f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was lower than',
                    _CHECK_['Shell']['Keel'], '. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness_empi = _CHECK_['Shell']['Keel']
            else:
                if Debug: c_info((
                    f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was greater than',
                    _CHECK_['Shell']['Keel']))
        else:
            if plate.plate.net_thickness_empi < _CHECK_['Shell']['Else']:
                if Debug: c_info((
                    f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was lower than',
                    _CHECK_['Shell']['Else'], '. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness_empi = _CHECK_['Shell']['Else']
            else:
                if Debug: c_info((
                    f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was greater than',
                    _CHECK_['Shell']['Else']))
    elif plate.tag == 1:
        if plate.plate.net_thickness_empi < _CHECK_['InnerBottom']:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was lower than',
                _CHECK_['InnerBottom'], '. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness_empi = _CHECK_['InnerBottom']
        else:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was greater than',
                _CHECK_['InnerBottom']))
    elif plate.tag in (2, 3):  # and ship.type == 'BulkCarrier': #(later implement)
        if plate.plate.net_thickness_empi < _CHECK_['Hopper/Wing-BC']:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was lower than',
                _CHECK_['Hopper/Wing-BC'], '. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness_empi = _CHECK_['Hopper/Wing-BC']
        else:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was greater than',
                _CHECK_['OtherPlates']))
    elif plate.tag == 5:
        if plate.plate.net_thickness_empi < _CHECK_['Deck']:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was lower than',
                _CHECK_['Deck'], '. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness_empi = _CHECK_['Deck']
        else:
            if Debug: c_info((
                f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness_empi} was greater than',
                _CHECK_['Deck']))
    else:
        c_error(f'(rules.py) minimum_plate_net_thickness: Plate {plate}. You are not supposed to enter here.')


def minimum_stiff_net_thickness(plate: cls.StiffPlate, L2: float, Debug=False):
    '''
    -----------------------------------------
    IACS Part 1 Chapter 6 Section 3.2
    Table 2
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.\n
    To be called explicitly after checking the respective stiffened plate's plate.
    '''
    _CHECK_ = {
        'Longs': {
            'Watertight': (3.5 + 0.015 * L2) * 1e-3,
            'Else': (3.0 + 0.015 * L2) * 1e-3
        }
    }

    # must calculate first its pressure thickness
    sup = 2.0 * plate.plate.net_thickness
    base = max(_CHECK_['Longs']['Watertight'], 0.4 * plate.plate.net_thickness)
    update = False
    if plate.stiffeners[0].type == 'fb':
        stiff = plate.stiffeners[0]
        if (stiff.plates[0].net_thickness_empi < base) and (stiff.plates[
                                                                0].net_thickness_empi < sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[0].net_thickness_empi = base
            update = True
        elif (stiff.plates[0].net_thickness_empi > base) and (stiff.plates[
                                                                  0].net_thickness_empi > sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[0].net_thickness_empi = sup
            update = True
        else:
            if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
    elif plate.stiffeners[0].type in ('g', 'tb'):
        stiff = plate.stiffeners[0]
        if (stiff.plates[0].net_thickness_empi < base) and (stiff.plates[
                                                                0].net_thickness_empi < sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[0].net_thickness_empi = base
            update = True
        elif (stiff.plates[0].net_thickness_empi > base) and (stiff.plates[
                                                                  0].net_thickness_empi > sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[0].net_thickness_empi = sup
            update = True
        else:
            if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
        if (stiff.plates[1].net_thickness_empi < base) and (stiff.plates[
                                                                1].net_thickness_empi < sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was lower than', base,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[1].net_thickness_empi = base
            update = True
        elif (stiff.plates[1].net_thickness_empi > base) and (stiff.plates[
                                                                  1].net_thickness_empi > sup):  # For the time being every Longitudinal is on a watertight plate
            if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was greater than', sup,
                              '. Thus it was changed to the appropriate value'))
            stiff.plates[1].net_thickness_empi = sup
            update = True
        else:
            if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Flange plate thickness was within limits'))

    else:
        c_error(f'(rules.py) minimum_stiff_net_thickness: Plate {plate}. You are not supposed to enter here.')
    if update:
        if plate.stiffeners[0].type == 'fb':
            for stiff in plate.stiffeners[1:]:
                stiff.plates[0].net_thickness_empi = plate.stiffeners[0].plates[0].net_thickness_empi
        elif plate.stiffeners[0].type in ('g', 'tb'):
            for stiff in plate.stiffeners[1:]:
                stiff.plates[0].net_thickness_empi = plate.stiffeners[0].plates[0].net_thickness_empi
                stiff.plates[1].net_thickness_empi = plate.stiffeners[0].plates[1].net_thickness_empi


def plating_net_thickness_calculation(ship: cls.Ship, plate: cls.StiffPlate, case: phzx.PhysicsData,
                                      Dynamic=False, Debug=False):
    '''
    IACS Part 1 Chapter 6 Section 4\n

    '''

    # application point to be on the stiffeners
    x = {
        0: 1.0,  # "Shell"
        1: 0.7,  # 'InnerBottom'
        2: 0.7,  # 'Hopper'
        3: 1.0,  # 'Wing'
        4: 1.0,  # 'Bilge'
        5: 1.0  # 'WeatherDeck'
    }
    ap = 1.2 - plate.spacing ** 2 / 2.1 / plate.PSM_spacing
    try:
        Reh, Rem, Teh = MATERIALS[plate.plate.material]
    except KeyError:
        c_warn(
            f'(rules.py) plating_thickness_calculation: Stiffened plate\'s plate {plate} has material {plate.plate.material} that is not documented in this program. Either consider changing it or modify constants.py MATERIALS dict. Defaulting to A grade steel (Rm = 255)...')

    def Ca(point):
        if Dynamic:
            Ca = min(0.9 - 0.5 * abs(case.sigma(*point)) / Reh, 0.8)
        else:
            Ca = min(1.05 - 0.5 * abs(case.sigma(*point)) / Reh, 0.95)

        if Ca < 0:
            if Debug: c_warn(
                f'(rules.py) plating_thickness_calculation/Ca: Ca coefficient has been found negative! '
                f'This is due to having an extremely low Area Moment of Inertia.\n '
                f'I assume that this is the first design circle and therefore Ca_max will be used!')
            if Dynamic:
                Ca = 0.8
            else:
                Ca = 0.95
        return Ca

    t = lambda point, P: 0.0158 * ap * plate.spacing * math.sqrt(abs(P) / x[plate.tag] / Ca(point) / Reh)
    max_t = 0
    if Debug: c_info(f'net_plating plate:{plate}')
    try:
        for i, data in enumerate(plate.Pressure[case.cond]):
            point = (data[0], data[1])
            P = data[-1]
            if Debug: c_info(f'Press : {P},Point: {point},sigma {abs(case.sigma(*point))},Ca {Ca(point)}',
                             default=False)
            t_temp = t(point, P)
            if Debug: c_info(f't_temp:{t_temp}', default=False)
            max_t = t_temp if max_t < t_temp else max_t
        if Debug: c_info(f', max_t:{max_t}', default=False)
    except KeyError:
        c_warn(
            f'(rules.py) plating_thickness_calculation: The {case.cond} '
            f'condition has not been calculated for  plate {plate}. Checking only the empirical thickness value...')
        minimum_plate_net_thickness(plate, L2=min(300, case.Lsc), Debug=Debug)
        return None
        # Special Cases
    if (plate.tag == 0) and ((ship.Tmin < plate.plate.start[1] < 1.25 * ship.Tsc)
                             or (ship.Tmin < plate.plate.end[1] < 1.25 * ship.Tsc)):
        t = 26 * (plate.spacing + 0.7) * (ship.B * ship.Tsc / Reh ** 2) ** 0.25 * 1e-3  # m
        if Debug: c_info(
            f'(rules.py) plating_thickness_calculation: Plate {plate} '
            f'Contact Fender Zone special t {t * 1e3} while local scantlings t {max_t * 1e3} [mm]')
    elif plate.tag == 4:
        P = plate.Pressure[case.cond][0][-1]
        R = abs(plate.plate.start[1] - plate.plate.end[1]) + 0.5 * (plate.s_pad + plate.e_pad)
        t = 6.45 * (P * plate.PSM_spacing * 1e3) ** (0.4) * (R * 1e3) ** (0.6) * 1e-7  # m
        if Debug: c_info(
            f'(rules.py) plating_thickness_calculation: Plate {plate} '
            f'Bilge Zone special t {t * 1e3} while local scantlings t {max_t * 1e3} [mm]')
    else:
        t = 0
    # t=0
    if plate.plate.net_thickness_calc < max(t, max_t):
        plate.plate.net_thickness_calc = max(t, max_t)
        # program some checks according to Chapter 6, Section 4.2 page 383

    minimum_plate_net_thickness(plate, L2=min(300, case.Lsc), Debug=Debug)  # need to check what L2 is
    plate.update()


def stiffener_plating_net_thickness_calculation(plate: cls.StiffPlate,
                                                case: phzx.PhysicsData,
                                                dynamic=False,
                                                debug=False):
    """
    IACS Part 1 Chapter 6, Section 4
    """
    try:
        Reh, Rem, Teh = MATERIALS[plate.stiffeners[0].plates[0].material]
    except KeyError:
        c_warn(
            f'(rules.py) plating_thickness_calculation: Stiffened plate\'s plate {plate} has material {plate.plate.material} that is not documented in this program. Either consider changing it or modify constants.py MATERIALS dict. Defaulting to A grade steel (Rm = 255)...')
    x = {
        0: 1.0,  # "Shell"
        1: 0.9,  # 'InnerBottom'
        2: 0.9,  # 'Hopper'
        3: 1.0,  # 'Wing'
        4: 1.0,  # 'Bilge'
        5: 1.0  # 'WeatherDeck'
    }
    Ct_ = {
        'AC-S': 0.75,
        'AC-SD': 0.90
    }
    Ct = Ct_['AC-S'] if dynamic else Ct_['AC-SD']

    def Cs(sigma):
        if dynamic:  # AC-S
            if sigma >= 0:
                return 0.75
            else:
                return 0.85 - abs(sigma) / Reh
        else:  # AC-SD
            if sigma >= 0:
                return 0.9
            else:
                return 1.0 - abs(sigma) / Reh

    dshr = (plate.plate.length + plate.stiffeners[0].plates[0].net_thickness + 0.5 * plate.plate.cor_thickness - 0.5 *
            plate.stiffeners[0].plates[
                0].net_thickness) * 1.0  # hardcoded that phiw = 90 deg This is a critical assumption

    fshr = 0.7  # lower end of vertical stiffeners is the minimum worst condition
    fbdg = 12  # horizontal stiffeners

    lbdg = plate.PSM_spacing  # worst case scenario dont know the stiffener span
    lshr = plate.PSM_spacing - plate.spacing / 2  # worst case scenario dont know the stiffener span
    tw = lambda P: (fshr * abs(P) * plate.spacing * lshr) / (dshr * x[plate.tag] * Ct * Teh) * 1e-3
    Z = lambda P, point: (abs(P) * plate.spacing * 1e3 * lbdg ** 2) / (
            fbdg * x[plate.tag] * Cs(case.sigma(*point)) * Reh) * 1e-6

    max_t = 0
    max_Z = 0
    P = 0
    for i, stiff in enumerate(plate.stiffeners):
        try:
            P = plate.local_P(case.cond, stiff.plates[0].start)
        except KeyError:
            c_warn(
                f'(rules.py) stiffener_plating_thickness_calculation: The {case.cond} condition has not been calculated for this plate. Checking only the empirical thickness value...')
            break
        t_tmp = tw(P)
        if max_t < t_tmp:
            max_t = t_tmp
    if plate.stiffeners[0].plates[0].net_thickness_calc < max_t:
        for stiff in plate.stiffeners:
            if len(stiff.plates) > 1:
                for p in stiff.plates:
                    p.net_thickness_calc = max_t
            stiff.plates[0].net_thickness_calc = max_t

    minimum_stiff_net_thickness(plate, min(300, case.Lsc), Debug=debug)
    plate.update()
    for i, stiff in enumerate(plate.stiffeners):
        Z_tmp = Z(P, stiff.plates[0].start)
        if max_Z < Z_tmp:
            max_Z = Z_tmp
    Z_local = plate.stiffeners[0].calc_Z()
    if max_Z > plate.stiffeners[0].Z_rule:
        for i in plate.stiffeners:
            i.Z_rule = max_Z

    if max_Z > Z_local:
        c_warn(
            f'(rules.py) stiffener_plating_net_thickness_calculation: Plate {plate} Z is less than Z calculated by regulations ({Z_local * 1e6} < {max_Z * 1e6})')
        c_warn(f'Consider fixing it manually, as an automatic solution is not currently possible.')


def buckling_evaluator(ship: cls.Ship, Debug=False):
    """
    IACS PART 1 CHAPTER 8 SECTION 2
    Slenderness requirements 
    """
    CwCf = {
        'fb': (22,),
        'bb': (45,),
        'tb': (75, 12),
        'g': (75, 12)
    }
    C = 1.43  # longitudinals
    if Debug: print('Buckling check')
    for st_plate in ship.stiff_plates:
        if Debug: print(st_plate)
        if len(st_plate.stiffeners) > 0 and st_plate.tag not in (4, 6):
            Reh = min(MATERIALS[st_plate.plate.material][0], MATERIALS[st_plate.stiffeners[0].material][0])
        else:
            continue
        N = len(st_plate.stiffeners)
        Aeff = N * st_plate.stiffeners[0].area + st_plate.plate.thickness * st_plate.b_eff  # m^2
        Ist = N * C * st_plate.PSM_spacing ** 2 * Aeff * Reh / 235 * 1e-4  # m^4

        # thickness check
        tp = st_plate.b_eff / 100 * math.sqrt(Reh / 235)

        if Debug: print('b_eff: ', st_plate.b_eff)
        if Debug: print('tp: ', tp)
        if st_plate.plate.net_thickness_calc < tp:
            if st_plate.plate.net_thickness < tp: c_warn(
                f'(rules.py) buckling_evaluator: Available tp: {st_plate.plate.net_thickness * 1e3} mm is less than minimum tp: {tp * 1e3} mm by the rules for plate {st_plate} ')
            st_plate.plate.net_thickness_calc = tp
        tw = st_plate.stiffeners[0].plates[0].length / CwCf[st_plate.stiffeners[0].type][0] * math.sqrt(Reh / 235)
        if Debug: print('tw: ', tw)
        if st_plate.stiffeners[0].plates[0].net_thickness_buck < tw:
            if st_plate.stiffeners[0].plates[0].net_thickness < tw: c_warn(
                f'(rules.py) buckling_evaluator: Available tw: {st_plate.stiffeners[0].plates[0].net_thickness * 1e3} mm is less than minimum tw: {tw * 1e3} mm by the rules for plate {st_plate} ')
            st_plate.stiffeners[0].plates[0].net_thickness_buck = tw
        if st_plate.stiffeners[0].type in ('tb', 'g'):
            tf = (math.sqrt((st_plate.stiffeners[0].plates[1].end[0] - st_plate.stiffeners[0].plates[0].end[0]) ** 2
                            + (st_plate.stiffeners[0].plates[1].end[1] - st_plate.stiffeners[0].plates[0].end[1]) ** 2)
                  / CwCf[st_plate.stiffeners[0].type][1] * math.sqrt(Reh / 235))
            if Debug: print('tf: ', tf)
            if st_plate.stiffeners[0].plates[1].net_thickness_buck < tf:
                if st_plate.stiffeners[0].plates[1].net_thickness < tf: c_warn(
                    f'(rules.py) buckling_evaluator: Available tf: {st_plate.stiffeners[0].plates[1].net_thickness * 1e3} mm is less than minimum tf: {tf * 1e3} mm by the rules for plate {st_plate} ')
                st_plate.stiffeners[0].plates[1].net_thickness_buck = tf
        # Area Moment check
        st_plate.update()

        if Debug: print('Ist: ', Ist, 'Ieff: ', st_plate.Ixx_c)
        if st_plate.Ixx_c < Ist:
            c_warn(
                f'(rules.py) buckling_evaluator: Available Ieff: {st_plate.Ixx_c} is less than minimum Ieff: {Ist} by the rules for plate {st_plate} ')
        ship.update()


# ----------------  Loading cases manager function  ----------------------------
def Loading_cases_eval(ship: cls.Ship, case: phzx.PhysicsData, condition: dict):
    '''
    condition = {
        'Dynamics':'SD',
        'max value': 'DC,WB',
        'skip value':'LC'
    }
    '''

    def maximum_P(P):
        def key(list):
            return abs(list[-1])

        max_p = 0
        index = 0
        for i, P_ in enumerate(P):
            local_max = max(P_, key=key)
            if max_p < local_max[-1]:  # Pressure position
                max_p = local_max[-1]
                index = i
        return index

    for plate in ship.stiff_plates:
        if plate.null or plate.tag == 6: continue  # skip calculation for null plates and girders
        blocks = []
        max_eval = False
        for block in ship.blocks:
            if (plate.id in block.list_plates_id or -plate.id in block.list_plates_id) and block.space_type not in \
                    condition['skip value']:
                blocks.append(block)
            elif (plate.id in block.list_plates_id or -plate.id in block.list_plates_id) and block.space_type in \
                    condition['skip value']:
                # use a zero pressure pseudo block as the plate is well defined and raising an exception is unwanted behavior
                zero = cls.Block('zero', False, 'VOID', [plate.id, ])
                zero.get_coords([plate, ])
                zero.Pressure[case.cond] = [0 for i in zero.pressure_coords]
                blocks.append(zero)
        if len(blocks) > 2:
            c_error(
                f'(rules.py) Loading_cases: Detected a plate: {plate} which is contained in multiple blocks. A stiffened plate can be boundary of only 2 Blocks at most at a time!')
            c_error(f'Involved Blocks:\n {blocks}')
            quit()
        elif len(blocks) == 0:
            c_error(
                f'(rules.py) Loading_cases: Detected a plate: {plate} which is contained in no blocks. A stiffened plate shall be boundary to at least one Block !')
            quit()

        for block in blocks:
            if block.space_type in condition['max value'] and not max_eval:
                max_eval = True
        if max_eval:
            P = []
            for block in blocks:
                P.append(phzx.block_to_plate_per_case(plate, [block], case, condition['Dynamics'],
                                                      return_=True))  # force the singular evaluation of each pressure distribution
            # if plate.id in (3,1,2):c_info(f'plate: {plate}\nmax_eval: {P}')
            index = maximum_P(P)
            plate.Pressure[case.cond] = P[index]
        else:
            phzx.block_to_plate_per_case(plate, blocks, case,
                                         condition['Dynamics'])  # let the function handle the proper aggregation
        # if plate.id in (3,1,2):c_info(f'plate: {plate}\nAGG_eval: {plate.Pressure[case.cond]}')
        plate.datacell.update(plate)  # save pressure maximum pressure data


def ship_scantlings(ship: cls.Ship):
    In50 = 2.7 * ship.Cw * ship.Lsc ** 3 * ship.B * (ship.Cb + 0.7) * 1e-8
    Zrn50 = 0.9 * ship.kappa * ship.Cw * ship.Lsc ** 2 * ship.B * (
            ship.Cb + 0.7) * 1e-6  # k = 1.0 Grade A steel(not a good idea, pretty retarded)
    Zn50k_ship = ship.n50_Ixx / (ship.yo)
    Zn50d_ship = ship.n50_Ixx / abs(ship.yo - ship.D)
    c_info(f'(rules.py) ship_scantlings: The ship\'s neutral axis is at {ship.yo:0.5g} meters from Keel')
    if ship.n50_Ixx < In50:
        c_warn(
            f'(rules.py) ship_scantlings: The Area Inertia Moment of the ship In50 : {ship.n50_Ixx:0.5g} is less than In50: {In50:0.5g} calculated by the rules')
    else:
        c_success(
            f'(rules.py) ship_scantlings: The Area Inertia Moment of the ship In50 : {ship.n50_Ixx:0.5g} is adequate compared to In50: {In50:0.5g} calculated by the rules')
    if Zn50k_ship < Zrn50:
        c_warn(
            f'(rules.py) ship_scantlings: The Section Modulus at Keel of the ship Zn50,keel : {Zn50k_ship:0.5g} is less than Zrn50: {Zrn50:0.5g} calculated by the rules')
    else:
        c_success(
            f'(rules.py) ship_scantlings: The Section Modulus at Keel of the ship Zn50,keel : {Zn50k_ship:0.5g} is adequate compared to Zrn50: {Zrn50:0.5g} calculated by the rules')
    if Zn50d_ship < Zrn50:
        c_warn(
            f'(rules.py) ship_scantlings: The Section Modulus at Depth of the ship Zn50,Depth : {Zn50d_ship:0.5g} is less than Zrn50: {Zrn50:0.5g} calculated by the rules')
    else:
        c_success(
            f'(rules.py) ship_scantlings: The Section Modulus at Depth of the ship Zn50,Depth : {Zn50d_ship:0.5g} is adequate compared to Zrn50: {Zrn50:0.5g} calculated by the rules')


def net_scantling(ship: cls.Ship, case: phzx.PhysicsData, Dynamics: str, Debug=True):
    if 'd' in Dynamics or 'D' in Dynamics:
        _Dynamic = True
    else:
        _Dynamic = False
    for stiff_plate in ship.stiff_plates:
        if stiff_plate.null or stiff_plate.tag == 6: continue  # skip calculation for null plates and girders
        if Debug: c_info(f'(rules.py) net_scantling: Evaluating plate\'s :{stiff_plate} PLATES NET SCANTLING')
        plating_net_thickness_calculation(ship, stiff_plate, case, Dynamic=_Dynamic, Debug=Debug)
        if Debug: c_info(f'(rules.py) net_scantling: Evaluated plate\'s :{stiff_plate} PLATES NET SCANTLING')
    ship.update()
    for stiff_plate in ship.stiff_plates:
        if stiff_plate.null or stiff_plate.tag == 6: continue  # skip calculation for null plates and girders
        if Debug: c_info(f'(rules.py) net_scantling: Evaluating plate\'s {stiff_plate} STIFFENERS NET SCANTLING')
        if len(stiff_plate.stiffeners) != 0:  # Bilge plate and other loose plates
            stiffener_plating_net_thickness_calculation(stiff_plate, case, dynamic=_Dynamic, debug=Debug)
    ship.update()


def corrosion_addition(stiff_plate: cls.StiffPlate, blocks: list[cls.Block], Tmin, Tmax):
    # CSR Chapter 1 Section 3
    Corr = {
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
        'in': 0,
        'out': 0,
    }
    if len(tags) == 0:
        c_warn((f'(rules.py) corrosion_addition:/ Stiffened plate\'s {stiff_plate} locality data are not present.'
                'Resetting to the Hopper case for both sides'))
        plate_t_corr['in'] = Corr["CHP"]["Hopper/InBot"]
        plate_t_corr['out'] = Corr["CHP"]["Hopper/InBot"]
        return plate_t_corr

    if stiff_plate.tag in (0, 4):  # Shell plates
        Y = max(stiff_plate.plate.start[1], stiff_plate.plate.end[1])
        if Y <= Tmin:
            plate_t_corr['out'] = Corr['X2SW']['Wet']
        elif Y > Tmin and Y < Tmax:
            plate_t_corr['out'] = Corr['X2SW']['Wet/Dried']
        elif Y > Tmax:
            plate_t_corr['out'] = Corr['X2A']['WeatherDeck']  # Is it tho ?

        t_in = 0
        for i in tags:
            if "WB" == i:
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top']: t_in = Corr['WBT']['FacePlate']['=< 3,tank_top']
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"]: t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"]: t_in = Corr["Misc"]["DrySpace"]

        plate_t_corr['in'] = t_in

    elif stiff_plate.tag in (1, 2, 3):  # Inner Bottom, Hopper, Wing
        t = [0, 0]
        ind = 0
        c = 0
        if len(tags) == 1:
            c_warn((f'(rules.py) corrosion_addition:/ Stiffened plate\'s {stiff_plate} locality data are inadequate.'
                    'Using the data of the one side for both sides ...'))
            tags.append(tags[0])
        while c <= 1:  # not the best way but oh well
            for i, tag in enumerate(tags):
                if "WB" == tag:
                    if t[c] < Corr['WBT']['FacePlate']['=< 3,tank_top']:
                        t[c] = Corr['WBT']['FacePlate']['=< 3,tank_top']
                        ind = i
                elif 'DC' == tag:
                    if t[c] < Corr["CHP"]["Hopper/InBot"]:
                        t[c] = Corr["CHP"]["Hopper/InBot"]
                        ind = i
                elif 'OIL' == tag or 'FW' == tag:
                    if t[c] < Corr["Misc"]["FO/FW/LO/VS"]:
                        t[c] = Corr["Misc"]["FO/FW/LO/VS"]
                        ind = i
                elif 'VOID' == tag:
                    if t[c] < Corr["Misc"]["DrySpace"]:
                        t[c] = Corr["Misc"]["DrySpace"]
                        ind = i
            tags.pop(ind)
            c += 1
        # No respect for the actual geometry but I 'ld rather over-engineer stiffener scantlings
        plate_t_corr['in'] = max(t)
        plate_t_corr['out'] = min(t)


    elif stiff_plate.tag == 5:  # Weather Deck
        plate_t_corr['out'] = Corr["X2A"]["WeatherDeck"]
        t_in = 0
        for i in tags:
            if "WB" == i:
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top']: t_in = Corr['WBT']['FacePlate']['=< 3,tank_top']
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"]: t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"]: t_in = Corr["Misc"]["DrySpace"]

        plate_t_corr['in'] = t_in

    return plate_t_corr


def corrosion_assign(ship: cls.Ship, input: bool):
    '''
    Data input assumes gross thickness scantling.\n
    Input = True, offloads the corrosion addition to assign the net scantling
    Input = False, loads the corrosion addition to assign the new gross scantling
    '''

    def round_to_p5(num):
        return math.ceil(num * 2) / 2

    if input:
        for stiff_plate in ship.stiff_plates:
            if stiff_plate.null or stiff_plate.tag == 6: continue  # skip calculation for null plates and girderss and girders
            c_t = corrosion_addition(stiff_plate, ship.blocks, ship.Tmin, ship.Tsc)
            stiff_plate.plate.cor_thickness = (round_to_p5(c_t['in'] + c_t['out']) + 0.5) * 1e-3
            stiff_plate.plate.net_thickness = stiff_plate.plate.thickness - stiff_plate.plate.cor_thickness
            if stiff_plate.plate.net_thickness < 0: stiff_plate.plate.net_thickness = 1e-3  # maybe redundant but a good sanity check
            for stiffener in stiff_plate.stiffeners:
                for plate in stiffener.plates:
                    plate.cor_thickness = (round_to_p5(c_t['out'] + c_t['in']) + 0.5) * 1e-3
                    plate.net_thickness = plate.thickness - plate.cor_thickness
                    if plate.net_thickness < 0: plate.net_thickness = 1e-3
    else:
        for stiff_plate in ship.stiff_plates:
            if stiff_plate.null or stiff_plate.tag == 6: continue  # skip calculation for null plates and girderss and girders
            if stiff_plate.plate.cor_thickness < 0:
                c_error(
                    f'(rules.py) corrosion_assign: Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!')
                quit()
            stiff_plate.plate.thickness = stiff_plate.plate.net_thickness + stiff_plate.plate.cor_thickness
            for stiffener in stiff_plate.stiffeners:
                for plate in stiffener.plates:
                    if plate.cor_thickness < 0:
                        c_error(
                            f'(rules.py) corrosion_assign: Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!')
                        quit()
                    plate.thickness = plate.net_thickness + plate.cor_thickness
