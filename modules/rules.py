# #############################
# CSR Rules and Regulations for Dry Cargo
# #############################

#Materials Constant Array see. CSR ... to be filled
import math

import modules.classes as cls
import modules.physics as phzx
from modules.utilities import c_error, c_info, c_warn
from modules.constants import MATERIALS

# page 378 the application table
#------------------- Thickness Calculation Functions --------------------------
def minimum_plate_net_thickness(plate:cls.stiff_plate,L2:float,Debug = False):
    '''
    -----------------------------------------
    IACS Part 1 Chapter 6 Section 3.1
    Table 1
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.
    '''
    _CHECK_ = {
        'Shell':{
            'Keel': (7.5 + 0.03*L2)*1e-3,
            'Else': (5.5 + 0.03*L2)*1e-3
        },
        'Deck': (4.5 + 0.02*L2)*1e-3,
        'InnerBottom': (5.5 + 0.03*L2)*1e-3,
        'OtherPlates': (4.5 + 0.01*L2)*1e-3
    }

    if plate.tag in (0,4):
        if plate.plate.start[0] == 0: # keel plate
            if plate.plate.net_thickness < _CHECK_['Shell']['Keel']:
                if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was lower than', _CHECK_['Shell']['Keel'],'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  _CHECK_['Shell']['Keel']
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was greater than',_CHECK_['Shell']['Keel']))
        else:
            if plate.plate.net_thickness < _CHECK_['Shell']['Else']:
                if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was lower than', _CHECK_['Shell']['Else'],'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  _CHECK_['Shell']['Else']
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was greater than',_CHECK_['Shell']['Else']))
    elif plate.tag in (2,1):
        if plate.plate.net_thickness < _CHECK_['InnerBottom']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was lower than', _CHECK_['InnerBottom'],'. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness =  _CHECK_['InnerBottom']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was greater than',_CHECK_['InnerBottom']))
    elif plate.tag == 3:
        if plate.plate.net_thickness < _CHECK_['OtherPlates']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was lower than', _CHECK_['OtherPlates'],'. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness =  _CHECK_['OtherPlates']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was greater than',_CHECK_['OtherPlates']))
    elif plate.tag == 5:
        if plate.plate.net_thickness < _CHECK_['Deck']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was lower than', _CHECK_['Deck'],'. Thus it was changed to the appropriate value'))
            plate.plate.net_thickness =  _CHECK_['Deck']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} net plate thickness {plate.plate.net_thickness} was greater than',_CHECK_['Deck']))
    else:
        c_error(f'(rules.py) minimum_plate_net_thickness: Plate {plate}. You are not supposed to enter here.')

def minimum_stiff_net_thickness(plate:cls.stiff_plate,L2:float,Debug = False):
    '''
    -----------------------------------------
    IACS Part 1 Chapter 6 Section 3.2
    Table 2
    -----------------------------------------
    The function checks whether the Rule defined minimum thicknesses are obtained and if not updates them.\n
    To be called explicitly after checking the respective stiffened plate's plate.
    '''
    _CHECK_ = {
        'Longs':{
            'Watertight': (3.5 + 0.015*L2)*1e-3,
            'Else': (3.0 + 0.015*L2)*1e-3
        }
    }

    # must calculate first its pressure thickness
    sup = 2.0*plate.plate.net_thickness
    base = max(_CHECK_['Longs']['Watertight'],0.4*plate.plate.net_thickness)

    if plate.stiffeners[0].type == 'fb': 
        for i,stiff in enumerate(plate.stiffeners):
            if (stiff.plates[0].net_thickness < base) and (stiff.plates[0].net_thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  base
            elif (stiff.plates[0].net_thickness > base) and (stiff.plates[0].net_thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
    elif plate.stiffeners[0].type == 'g':
        for i,stiff in enumerate(plate.stiffeners):
            if (stiff.plates[0].net_thickness < base) and (stiff.plates[0].net_thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  base
            elif (stiff.plates[0].net_thickness > base) and (stiff.plates[0].net_thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
            if (stiff.plates[1].net_thickness < base) and (stiff.plates[1].net_thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  base
            elif (stiff.plates[1].net_thickness > base) and (stiff.plates[1].net_thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.net_thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Flange plate thickness was within limits'))

    else:
        c_error(f'(rules.py) minimum_stiff_net_thickness: Plate {plate}. You are not supposed to enter here.')

    
def plating_net_thickness_calculation(ship:cls.ship,plate:cls.stiff_plate,case:phzx.PhysicsData,sloshing = False,Debug=False):
    '''
    IACS Part 1 Chapter 6 Section 4\n

    '''

    # application point to be on the stiffeners
    x = {
        0: 1.0 , #"Shell"
        1: 0.7 , #'InnerBottom'
        2: 0.7 , #'Hopper'
        3: 1.0 , #'Wing'
        4: 1.0 , #'Bilge'
        5: 1.0   #'WeatherDeck'
    }
    ap = 1.2 - plate.spacing**2/2.1/ship.PSM_spacing
    try:
        Reh, Rem,Teh = MATERIALS[plate.plate.material]
    except KeyError:
        c_warn(f'(rules.py) plating_thickness_calculation: Stiffened plate\'s plate {plate} has material {plate.plate.material} that is not documented in this program. Either consider changing it or modify constants.py MATERIALS dict. Defaulting to A grade steel (Rm = 255)...')
    # Ca_ = {
    #     'AC-S' : (lambda x: 0.9 - 0.5*abs(x)/Reh,0.8),
    #     'AC-SD': (lambda x: 0.9 - 0.5*abs(x)/Reh,1.0)
    # }
    def Ca(point):
        if sloshing:
            Ca = min(0.9 - 0.5*abs(case.sigma(*point))/Reh,0.8)
        else:
            Ca = min(0.9 - 0.5*abs(case.sigma(*point))/Reh,1.0)
        
        if Ca < 0:
            if Debug: c_warn(f'(rules.py) plating_thickness_calculation/Ca: Ca coefficient has been found negative! This is due to having an extremely low Area Moment of Inertia.\n I assume that this is the first design circle and therefore Ca_max will be used!')
            if sloshing:
                Ca = 0.8
            else:
                Ca = 1.0
        return Ca

    t = lambda point, P : 0.0158*ap*plate.spacing*math.sqrt(abs(P)/x[plate.tag]/Ca(point)/Reh)
    max_t = 0
    if Debug: c_info(f'net_plating plate:{plate}')
    for i,stif in enumerate(plate.stiffeners):
        P = plate.local_P(case.cond,stif.plates[0].start)
        if Debug: c_info(f'Press : {P},Stiff: {stif.plates[0].start},sigma {abs(case.sigma(*stif.plates[0].start))},Ca {Ca(stif.plates[0].start)}',default=False)
        t_temp = t(stif.plates[0].start,P)
        if Debug: c_info(f't_temp:{t_temp}',default=False)
        max_t = t_temp if max_t < t_temp else max_t
    if Debug:c_info(f', max_t:{ max_t}',default=False)

    if plate.plate.net_thickness < max_t:
        plate.plate.net_thickness = max_t
        #program some checks according to Chapter 6 Section 4.2 page 383
    minimum_plate_net_thickness(plate,case.Lsc,Debug=Debug) #need to check what L2 is

def stiffener_plating_net_thickness_calculation(ship:cls.ship,plate:cls.stiff_plate,case:phzx.PhysicsData,sloshing=False,Debug=False):
    '''
    IACS Part 1 Chapter 6 Section 4\n

    '''
    try:
        Reh, Rem,Teh = MATERIALS[plate.plate.material]
    except KeyError:
        c_warn(f'(rules.py) plating_thickness_calculation: Stiffened plate\'s plate {plate} has material {plate.plate.material} that is not documented in this program. Either consider changing it or modify constants.py MATERIALS dict. Defaulting to A grade steel (Rm = 255)...')
    x = {
        0: 1.0 , #"Shell"
        1: 0.9 , #'InnerBottom'
        2: 0.9 , #'Hopper'
        3: 1.0 , #'Wing'
        4: 1.0 , #'Bilge'
        5: 1.0   #'WeatherDeck'
    }
    Ct_ = {
        'AC-S' : 0.75,
        'AC-SD': 0.90
    }
    Ct = Ct_['AC-S'] if sloshing else Ct_['AC-SD']

    def Cs(sigma):
        if sloshing:#AC-S
            if sigma >= 0:
                return 0.75
            else:
                return 0.85 - abs(sigma)/Reh
        else:#AC-SD
            if sigma >= 0:
                return 0.9
            else:
                return 1.0 - abs(sigma)/Reh


    dshr = (plate.plate.length + plate.stiffeners[0].plates[0].net_thickness + 0.5*plate.plate.cor_thickness - 0.5*plate.stiffeners[0].plates[0].net_thickness)*1.0 #hardcoded that phiw = 90 deg This is a critical assumption

    fshr = 0.7 #lower end of vertical stiffeners is the minimum worst condition
    fbdg = 10  #lower end of vertical stiffeners is the minimum worst condition

    lbdg = ship.PSM_spacing #worst case scenario dont know the stiffener span
    lshr = ship.PSM_spacing #worst case scenario dont know the stiffener span
    tw = lambda P : (fshr*abs(P)*plate.spacing*lshr)/(dshr*x[plate.tag]*Ct*Teh)*1e-3
    Z  = lambda P,point : (abs(P)*plate.spacing*1e3*lbdg**2)/(fbdg*x[plate.tag]*Cs(case.sigma(*point))*Reh)*1e-6

    max_t = 0
    max_Z = 0
    for i, stiff in enumerate(plate.stiffeners):
        t_tmp = tw(plate.local_P(case.cond,stiff.plates[0].start))
        if max_t < t_tmp:
            max_t = t_tmp
    if plate.stiffeners[0].plates[0].net_thickness < max_t:
        for stiff in plate.stiffeners: 
            if len(stiff.plates)>1:
                for p in stiff.plates:
                    p.net_thickness = max_t
            stiff.plates[0].net_thickness = max_t
    plate.update()
            
    minimum_stiff_net_thickness(plate,case.Lsc,Debug=Debug)
    for i, stiff in enumerate(plate.stiffeners):
        Z_tmp = Z(plate.local_P(case.cond,stiff.plates[0].start),stiff.plates[0].start)
        if max_Z < Z_tmp:
            max_Z = Z_tmp
    Z_local = plate.stiffeners[0].calc_Z()[0]
    if max_Z> Z_local:
        c_warn(f'(rules.py) stiffener_plating_net_thickness_calculation: Plate {plate} Z is less than Z calculated by regulations ({Z_local*1e6} < {max_Z*1e6})')
        c_warn(f'Consider fixing it manually, as an automatic solution is not currently possible.')

#----------------  Loading cases manager function  ----------------------------
def Loading_cases_eval(ship:cls.ship,case:phzx.PhysicsData,condition:dict):
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
        for i,P_ in enumerate(P):
            local_max = max(P_,key=key)
            if max_p < local_max[-1]: #Pressure position 
                max_p = local_max[-1]
                index = i
        return index

    for plate in ship.stiff_plates:
        blocks = []
        max_eval = False
        for block in ship.blocks:
            if plate.id in block.list_plates_id and block.space_type not in condition['skip value']:
                blocks.append(block)
        if len(blocks)> 2: 
            c_error(f'(rules.py) Loading_cases: Detected a plate: {plate} which is contained in multiple blocks. A stiffened plate can be boundary of only 2 Blocks at most at a time!')
            c_error(f'Involved Blocks:\n {blocks}')
            quit()
        elif len(blocks)==0:
            c_error(f'(rules.py) Loading_cases: Detected a plate: {plate} which is contained in no blocks. A stiffened plate shall be boundary to at least one Block !')
            quit()

        for block in blocks:
            if block.space_type in condition['max value'] and not max_eval:
                max_eval=True
        if max_eval:
            P = []
            for block in blocks:
                P.append(phzx.block_to_plate_perCase(plate,[block],case,condition['Dynamics'],return_=True))# force the singular evaluation of each pressure distribution
            # if plate.id in (3,1,2):c_info(f'plate: {plate}\nmax_eval: {P}')
            index = maximum_P(P)
            plate.Pressure[case.cond] = P[index]
        else:
            phzx.block_to_plate_perCase(plate,blocks,case,condition['Dynamics']) # let the function handle the proper aggregation
            # if plate.id in (3,1,2):c_info(f'plate: {plate}\nAGG_eval: {plate.Pressure[case.cond]}')


def net_scantling(ship : cls.ship,case:phzx.PhysicsData,Debug = True):
    for stiff_plate in ship.stiff_plates:
        if Debug: c_info(f'(rules.py) net_scantling: Evaluating plate {stiff_plate}')
        plating_net_thickness_calculation(ship,stiff_plate,case,Debug=Debug)
    ship.update()
    for stiff_plate in ship.stiff_plates:
        if Debug: c_info(f'(rules.py) net_scantling: Evaluating plate {stiff_plate}')
        if len(stiff_plate.stiffeners) != 0: #Bilge plate and other loose plates
            stiffener_plating_net_thickness_calculation(ship,stiff_plate,case,Debug=Debug)
    ship.update()

def corrosion_addition(stiff_plate: cls.stiff_plate, blocks : list[cls.block], Tmin, Tmax  ):
    # CSR Chapter 1 Section 3
    Corr = {
        "WBT": {
            "FacePlate":{
                "=< 3,tank_top" : 2.0,
                "else":1.5},
            "OtherMembers":{
                "=< 3,tank_top" : 2.0,
                "else":1.5}
            },
        "CHP": {
            "UpperPart" : 1.8,
            "Hopper/InBot": 3.7
        },
        "X2A": {
            "WeatherDeck": 1.7,
            "Other":1.0
        },
        "X2SW":{
            "Wet/Dried": 1.5,
            "Wet": 1.0
        },
        "Misc":{
            "FO/FW/LO/VS":0.7,
            "DrySpace":0.5
        }

    }
    #Grab tags
    tags = []
    for i in blocks:
        if stiff_plate.id in i.list_plates_id:
            tags.append(i.space_type)
    plate_t_corr = {
        'in':0,
        'out':0,
    }
    if stiff_plate.tag in (0,4): #Shell plates
        Y = max(stiff_plate.plate.start[1],stiff_plate.plate.end[1])
        if Y <= Tmin:
            plate_t_corr['out'] = Corr['X2SW']['Wet']*1e-3
        elif Y > Tmin and Y < Tmax:
            plate_t_corr['out'] = Corr['X2SW']['Wet/Dried']*1e-3
        elif Y > Tmax :
            plate_t_corr['out'] = Corr['X2A']['WeatherDeck']*1e-3 #Is it tho ?

        t_in = 0
        for i in tags:
            if "WB" == i :
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top'] : t_in = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"] : t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"] : t_in = Corr["Misc"]["DrySpace"]
        
        plate_t_corr['in'] = t_in*1e-3

    elif stiff_plate.tag in (1,2,3): #Inner Bottom, Hopper, Wing
        t= (0,0)
        ind = 0
        c = 0 
        while c <= 1: #not the best way but oh well
            for tag,i in enumerate(tags):
                if "WB" == tag :
                    if t[c] < Corr['WBT']['FacePlate']['=< 3,tank_top'] : 
                        t[c] = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
                        ind = i
                elif 'DC' == tag:
                    if t[c] < Corr["CHP"]["UpperPart"]:
                        t[c] = Corr["CHP"]["UpperPart"]
                        ind = i
                elif 'OIL' == tag or 'FW' == tag:
                    if t[c] < Corr["Misc"]["FO/FW/LO/VS"] : 
                        t[c] = Corr["Misc"]["FO/FW/LO/VS"]
                        ind = i
                elif 'VOID' == tag:
                    if t[c] < Corr["Misc"]["DrySpace"] : 
                        t[c] = Corr["Misc"]["DrySpace"]
                        ind = i
            tags.pop(ind)
            c+=1
        # No respect for the actual geometry but I 'ld rather over-engineer stiffener scantlings
        plate_t_corr['in'] = max(t)*1e-3
        plate_t_corr['out'] = min(t)*1e-3


    elif stiff_plate.tag == 5: #Weather Deck
        plate_t_corr['out'] = Corr["X2A"]["WeatherDeck"]*1e-3
        t_in = 0
        for i in tags:
            if "WB" == i :
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top'] : t_in = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"] : t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"] : t_in = Corr["Misc"]["DrySpace"]

        plate_t_corr['in']= t_in*1e-3

    return  plate_t_corr

def corrosion_assign(ship:cls.ship,input:bool):
    '''
    Data input assumes gross thickness scantling.\n
    Input = True, offloads the corrosion addition to assign the net scantling
    Input = False, loads the corrosion addition to assign the new gross scantling
    '''
    if input:
        for stiff_plate in ship.stiff_plates:
            c_t = corrosion_addition(stiff_plate,ship.blocks,ship.Tmin,ship.Tsc)
            stiff_plate.plate.cor_thickness = c_t['in']+c_t['out']
            stiff_plate.plate.net_thickness = stiff_plate.plate.thickness - stiff_plate.plate.cor_thickness
            for stiffener in stiff_plate.stiffeners:
                for plate in stiffener.plates:
                    plate.cor_thickness = c_t['in']
                    plate.net_thickness = plate.thickness - plate.cor_thickness
    else:
        for stiff_plate in ship.stiff_plates:
            if stiff_plate.plate.cor_thickness < 0:
                c_error(f'(rules.py) corrosion_assign: Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!')
                quit()
            stiff_plate.plate.thickness = stiff_plate.plate.net_thickness + stiff_plate.plate.cor_thickness
            for stiffener in stiff_plate.stiffeners:
                for plate in stiffener.plates:
                    if plate.cor_thickness < 0:
                        c_error(f'(rules.py) corrosion_assign: Stiffened plate {stiff_plate} has not been evaluated for corrosion addition !!!')
                        quit()
                    plate.thickness = plate.net_thickness + plate.cor_thickness






