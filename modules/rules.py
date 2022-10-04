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


# # {'Reh' : 235, 'Rm' : 400}
# def scantling_req(st_plate : stiff_plate, ship : ship) :+
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
            'Keel': 7.5 + 0.03*L2,
            'Else': 5.5 + 0.03*L2
        },
        'Deck': 4.5 + 0.02*L2,
        'InnerBottom': 5.5 + 0.03*L2,
        'OtherPlates': 4.5 + 0.01*L2
    }

    if plate.tag in ('Shell','Bilge'):
        if plate.plate.start[0] == 0: # keel plate
            if plate.plate.thickness < _CHECK_['Shell']['Keel']:
                if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was lower than', _CHECK_['Shell']['Keel'],'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  _CHECK_['Shell']['Keel']
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was greater than',_CHECK_['Shell']['Keel']))
        else:
            if plate.plate.thickness < _CHECK_['Shell']['Else']:
                if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was lower than', _CHECK_['Shell']['Else'],'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  _CHECK_['Shell']['Else']
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was greater than',_CHECK_['Shell']['Else']))
    elif plate.tag in ('Hopper','InnerBottom'):
        if plate.plate.thickness < _CHECK_['InnerBottom']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was lower than', _CHECK_['InnerBottom'],'. Thus it was changed to the appropriate value'))
            plate.plate.thickness =  _CHECK_['InnerBottom']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was greater than',_CHECK_['InnerBottom']))
    elif plate.tag == 'Wing':
        if plate.plate.thickness < _CHECK_['OtherPlates']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was lower than', _CHECK_['OtherPlates'],'. Thus it was changed to the appropriate value'))
            plate.plate.thickness =  _CHECK_['OtherPlates']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was greater than',_CHECK_['OtherPlates']))
    elif plate.tag == 'WeatherDeck':
        if plate.plate.thickness < _CHECK_['Deck']:
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was lower than', _CHECK_['Deck'],'. Thus it was changed to the appropriate value'))
            plate.plate.thickness =  _CHECK_['Deck']
        else: 
            if Debug: c_info((f'Stiffened plate\'s : {plate} plate thickness was greater than',_CHECK_['Deck']))
    else:
        c_error('You are not supposed to enter here.')

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
            'WaterTight': 3.5 + 0.015*L2,
            'Else': 3.0 + 0.015*L2
        }
    }

    # must calculate first its pressure thickness
    sup = 2.0*plate.plate.thickness
    base = max(_CHECK_['Longs']['Watertight'],0.4*plate.plate.thickness)

    if plate.stiffeners[0].type == 'fb': 
        for i,stiff in enumerate(plate.stiffeners):
            if (stiff.plates[0].thickness < base) and (stiff.plates[0].thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  base
            elif (stiff.plates[0].thickness > base) and (stiff.plates[0].thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
    elif plate.stiffeners[0].type == 'g':
            if (stiff.plates[0].thickness < base) and (stiff.plates[0].thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  base
            elif (stiff.plates[0].thickness > base) and (stiff.plates[0].thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener Web plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Web plate thickness was within limits'))
            if (stiff.plates[1].thickness < base) and (stiff.plates[1].thickness < sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was lower than', base,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  base
            elif (stiff.plates[1].thickness > base) and (stiff.plates[1].thickness > sup): # For the time being every Longitudinal is on a watertight plate
                if Debug: c_info((f'Stiffened plate\'s : {plate} Stiffener  Flange plate thickness was greater than', sup,'. Thus it was changed to the appropriate value'))
                plate.plate.thickness =  sup
            else: 
                if Debug: c_info((f'Stiffened plate\'s : {plate}  Stiffener Flange plate thickness was within limits'))

    else:
        c_error('You are not supposed to enter here.')

    
def plating_net_thickness_calculation(ship:cls.ship,plate:cls.stiff_plate,case:phzx.PhysicalData,sloshing = False):
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
        Reh, Rem = MATERIALS[plate.plate.material]
    except KeyError:
        c_warn(f'(rules.py) plating_thickness_calculation()/: Stiffened plate\'s plate {plate} has material {plate.plate.material} that is not documented in this program. Either consider changing it or modify constants.py MATERIALS dict. Defaulting to A grade steel (Rm = 255)...')
    Ca_ = {
        'AC-S' : (lambda x: 0.9 - 0.5*abs(x)/Reh,0.8),
        'AC-SD': (lambda x: 0.9 - 0.5*abs(x)/Reh,1.0)
    }
    if sloshing:
        res = Ca_['AC-S']
        Ca = lambda point : max(res[0](case.sigma(*point)),res[1])
    else:
        res = Ca_['AC-SD']
        Ca = lambda point : max(res[0](case.sigma(*point)),res[1])

    t = lambda point, P : 0.0158*ap*plate.plate.length*math.sqrt(abs(P)/x[plate.tag]/Ca(point)/Reh)
    max_t = 0
    for i,stif in enumerate(plate.stiffeners):
        t_temp = t(stif.plates[0].start,P)
        max_t = t_temp if max_t < t_temp else max_t
    
    if plate.plate.thickness < max_t:
        plate.plate.thickness = max_t



    









def net_scantling(plate : cls.plate):
    return 0

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

    if stiff_plate.tag in (0,4): #Shell plates
        Y = max(stiff_plate.plate.start[1],stiff_plate.plate.end[1])
        if Y <= Tmin:
            plate_t_corr = Corr['X2SW']['Wet']
        elif Y > Tmin and Y < Tmax:
            plate_t_corr = Corr['X2SW']['Wet/Dried']
        elif Y > Tmax :
            plate_t_corr = Corr['X2A']['WeatherDeck'] #Is it tho ?

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
        
        plate_t_corr += t_in

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
        plate_t_corr = t[0]+t[1]

    elif stiff_plate.tag == 5: #Weather Deck
        plate_t_corr = Corr["X2A"]["WeatherDeck"]
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

        plate_t_corr += t_in
    return  plate_t_corr

def Conditions(ship: cls.plate,condition:str):
    def FullLoadCondition(stiff_plate:cls.stiff_plate):
        '''
        Static + Dynamic
        Shell,
        Dry,Liquid Cargo only Pin
        '''
        # P = []
        # for i in ship.blocks:
        #     if stiff_plate.id in i.list_plates_id:
        #         if i.space_type == 'DC':
                    # P = i.






