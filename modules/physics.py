"""
This module provides the functions that calculate the pressures applied on the plates
"""
import math
from utilities import c_error, c_success,c_warn,lin_int_dict
import classes as cls
#____ CONSTANTS ________
RHO_S = 1.025 # tn/m^3 sea water @ 17 Celsius
RHO_F = 0.997 # tn/m^3 fresh water @ 17 Celsius
G = 9.8063 # gravitational acceleration


def hydrostatic_pressure(z:float,Tlc:float,rho:float):
    '''
    Convention is that the zero is located at the keel plate
    '''
    if 0<=z :
        dT = Tlc - z  
        return rho*G*dT
    # elif 0<z and z>Tlc:
    #     return 0
    else:
        c_warn(f"physics.hydrostatic_pressure : Your input was invalid. The function returns by default 0\n \
            your input was ({z},{Tlc},{rho}) ")
        return 0

def external_loadsC(Tlc:float,ship:cls.ship,cond:str,rho = RHO_S):
    '''
    -------------------------------------------------------------------------------------------------------------------
    Function that holds data for the constants that need to be passed to the external forces calculating functions.
    Input:\n
        Tlc ->  <float> Loading Condition Draught\n
        ship ->  A ship class object\n
        cond -> <string> The target Forces Calculating Condition \n
        rho -> <float> Target water's density (default : sea water @ 17 Celsius)\n
    Output:
        A tuple containing:
        fxL, fps, fb, ft, rho, LBP, B, Cw, Lsc, Tlc, Draught
    -------------------------------------------------------------------------------------------------------------------
    '''
    fxL = 0.5 # As the middle section is the object of study
    fps = 1.0 # Extreme Loads Scenario pp. 180 (to fill the other cases)
    fbeta = {
        'HSM' :1.05,
        'FSM' :1.05,
        'BSR' :0.80,
        'BSP' :0.80,
        'HSA' :1.00,
        'OST' :1.00,
        'OSA' :1.00,
        'OTR' :1.00,
        'FAT' :1.00
    } # pp. 186 Part 1 Chapter 4 Section 4
    try:
        fb = fbeta[cond] 
    except KeyError:
        c_error("Invalid condition to study. Enter an appropriate Condition out of :")
        [c_error(f"{i}") for i in fbeta]
        c_error('Currently supported conditions are : HSM and BSP.\n The other conditions will result in invalid results')
        c_error('The Program Terminates...')
        quit()
        # maybe can return Null and force to loop? if i want interactive ((maybe?))

    if Tlc <= ship.Tsc: #pp. 180
        ft = Tlc/ship.Tsc
    else :
        c_error("Your current Draught must not exceed the Scantling Draught.\n The program Terminates....")
        quit()
    if ft <= 0.5: ft = 0.5

    return fxL, fps, fb, ft,rho,ship.LBP, ship.B, ship.Cw,ship.Lsc,Tlc, ship.D

def HSM_wave_pressure(cons_:list[float],_1_:bool,block:cls.block):
    '''
    Calculates the wave pressure in kPa over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the HSM-1 or HSM-2, taking the values True and False respectively
    '''
    fnl = 0.9 # @50% Lbp pp 197

    fxL, fps, fbeta, ft,rho,LBP, B, Cw,Lsc, Tlc, D = cons_

    fh = 3*(1.21-0.66*ft)
    
    kp = {
        0 : lambda fyb_: -0.25*ft*(1+fyb_),
        round(0.3-0.1*ft,4)  : -1,
        round(0.35-0.1*ft,4) :  1,
        round(0.8-0.2*ft,4)  :  1,
        round(0.9-0.2*ft,4)  : -1,
        1.0 : -1         
    }

    kp_c = 0

    ka = 1.0 #@50% Lbp, may introduced the entire formula later 
    l = 0.6*(1+ft)*LBP
    
    fyB = lambda x : 2*x/B
    fyz = lambda y,z : z/Tlc+fyB(y)+1
    Phs = lambda y,z : fbeta*fps*fnl*fh*fyz(y,z)*ka*kp_c*Cw*math.sqrt((l+Lsc-125)/LBP)

    Pw = [None]*len(block.pressure_coords)
    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    
    if block.space_type == 'SEA': # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            for i,point in enumerate(block.pressure_coords):#the last 3 coordinates pressure_are rent
                kp_c = lin_int_dict(kp,fxL,fyB(point[0]),suppress=True)
                # print(f'kp_c: {kp_c}')
                hw  = -1*Phs(B/2,Tlc)/rho/G
                if point[1] < Tlc :            
                    Pw[i] = max(-1*Phs(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho) #PW = PW,WL - ρg(z - TLC)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho) #PW = PW,WL - ρg(z - TLC)
                    print('------ Tlc < x < Tlc+hw----')
                    print("Wave height : ",hw)
                    print("Pw,wl : ",hw*rho*G)
                    print("Hydrostatic Pressure : ",hydrostatic_pressure(point[1],Tlc,rho))
                    print('---------------------------')
                else:
                    Pw[i] =0
        else:
            for i,point in enumerate(block.pressure_coords):
                kp_c = lin_int_dict(kp,fxL,fyB(point[0]),suppress=True)
                # print(f'kp_c: {kp_c}')
                hw  = Phs(B/2,Tlc)/rho/G
                if point[1] < Tlc :            
                    Pw[i] = max(Phs(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    print('------ Tlc < x < Tlc+hw----')
                    print("Wave height : ",hw)
                    print("Pw,wl : ",hw*rho*G)
                    print("Hydrostatic Pressure : ",hydrostatic_pressure(point[1],Tlc,rho))
                    print('---------------------------')
                else:
                    Pw[i]=0

    elif block.space_type == 'ATM':
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*LBP

        kp_c = lin_int_dict(kp,fxL,fyB(D),suppress=True)
        if _1_:
            hw  = -1*Phs(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                    Pw[i] = max(Pw[i],Pmin)
                Pw[i] *= x
        else:
            hw  = Phs(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                    Pw[i] = max(Pw[i],Pmin)
                Pw[i] *= x

    else:
        c_warn('Cannot evaluate External pressures for an internal block.')
    key = 'HSM-1' if _1_ else 'HSM-2'
    block.Pressure[key] = Pw
    return Pw

def BSP_wave_pressure(cons_:list[float],_1_:bool,block:cls.block,Port=True):
    '''
    Calculates the wave pressure over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the BSP-1 or BSP-2, taking the values True and False respectively
    Port -> indicates whether we are working on the Port or Starboard side, taking the values True and False respectively
    '''
    fnl = 0.8 # @50% Lbp pp 202
    
    fxL, fps, fbeta, ft,rho,LBP, B, Cw,Lsc, Tlc, D = cons_
    

    l = 0.2*(1+2*ft)*LBP
    
    fyB = lambda y : 2*y/B
    # for the time being it can be left like this as a symmetrical case focused on Port
    if Port:
        fyz = lambda y,z : 2*z/Tlc+2.5*fyB(y)+0.5 #worst case scenario 
    else:
        print('Dont mess with the Port Setting. For the time being...')
        pass
        
    Pbsp = lambda y,z : 4.5*fbeta*fps*fnl*fyz(y,z)*Cw*math.sqrt((l+Lsc-125)/LBP)

    Pw = [None]*len(block.pressure_coords)
    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    if block.space_type == 'SEA': # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            hw  = Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] < Tlc :            
                    Pw[i] = max(Pbsp(*point),-hydrostatic_pressure(point[1],Tlc,rho/G))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho/G)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho/G)
                else:
                    Pw[i]=0
        else:
            hw  = -Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] < Tlc :            
                    Pw[i] = max(-Pbsp(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                else:
                    Pw[i]=0
    elif block.space_type == 'ATM':
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*LBP

        hw  = Pbsp(B/2,Tlc)/rho/G
        if _1_:
            hw  = Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                Pw[i]*=x
        else:
            hw  = -Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                Pw[i]*=x
    if Port:
        key = 'BSP-1P' if _1_ else 'BSP-2P'
    else:
        key = 'BSP-1S' if _1_ else 'BSP-2S'

    block.Pressure[key] = Pw
    return Pw

def HSM_total_eval(ship:cls.ship,Tlc:float):
    hsm_con = external_loadsC(Tlc,ship,'HSM')
    for i in ship.blocks:
        if i.space_type == 'SEA' or i.space_type == 'ATM':
            for j in (True,False):
                Pd = HSM_wave_pressure(hsm_con,j,i)
                if None not in Pd:
                    HSM = 'HSM-1' if j else 'HSM-2'
                    c_success(f'{HSM} CASE STUDY:\nCalculated block: ',i)
                    c_success(' ---- X ----  ---- Y ----  ---- P ----',default=False)
                    [c_success(f'{round(i.pressure_coords[j][0],4): =11f}  {round(i.pressure_coords[j][1],4): =11f} {round(Pd[j],4): =11f}',default=False) for j in range(len(Pd))]
    
    return Pd

def BSP_total_eval(ship:cls.ship,Tlc:float):
    bsp_con = external_loadsC(Tlc,ship,'BSP')
    for i in ship.blocks:
        if i.space_type == 'SEA' or i.space_type == 'ATM':
            for j in (True,False):
                Pd = BSP_wave_pressure(bsp_con,j,i)
                if None not in Pd:
                    BSP = 'BSP-1' if j else 'BSP-2'
                    c_success(f'{BSP} CASE STUDY:\nCalculated block: ',i)
                    c_success(' ---- X ----  ---- Y ----  ---- P ----',default=False)
                    [c_success(f'{round(i.pressure_coords[j][0],4): =11f}  {round(i.pressure_coords[j][1],4): =11f} {round(Pd[j],4): =11f}',default=False) for j in range(len(Pd))]

