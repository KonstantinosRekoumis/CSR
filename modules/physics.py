"""
This module provides the functions that calculate the pressures applied on the plates
"""
import math
from turtle import st
from utilities import c_error,c_warn,lin_int_dict
import classes as cls
#____ CONSTANTS ________
RHO_S = 1.025 # sea water @ 17 Celsius
RHO_F = 0.997 # fresh water @ 17 Celsius
G = 9.8063 # gravitational acceleration


def hydrostatic_pressure(z:float,T:float,rho:float):
    '''
    Convention is that the zero is located at the keel plate
    '''
    if 0<z and z<T:
        dT = T - z
        return rho*G*dT
    elif 0<z and z>T:
        return 0
    else:
        c_warn("Your input was invalid. The function returns by default 0")
        return 0

def external_loadsC(Tlc:float,ship:cls.ship,cond:str):
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

    return fxL, fps, fb, ft

def HSM_wave_pressure(_1_:bool,Tlc:float,rho:float,ship:cls.ship,stiff_plate:cls.stiff_plate):
    '''
    Calculates the wave pressure in kPa over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the HSM-1 or HSM-2, taking the values True and False respectively
    '''
    fnl = 0.9 # @50% Lbp pp 197

    fxL, fps, fbeta, ft = external_loadsC(Tlc,ship,'HSM')

    fh = 3*(1.21-0.66*ft)
    
    kp = {
        0 : lambda x: -0.25*ft*(1+x),
        round(0.3-0.1*ft,4)  : -1,
        round(0.35-0.1*ft,4) :  1,
        round(0.8-0.2*ft,4)  :  1,
        round(0.9-0.2*ft,4)  : -1,
        1.0 : -1         
    }

    kp_c = lin_int_dict(kp,fxL)

    ka = 1.0 #@50% Lbp, may introduced the entire formula later 
    l = 0.6*(1+ft)*ship.LBP
    
    fyB = lambda x : 2*x/ship.B
    fyz = lambda x,y : x/Tlc+fyB(y)+1
    Phs = lambda x,y : fbeta*fps*fnl*fh*fyz(x,y)*ka*kp_c*ship.Cw*math.sqrt((l+ship.Lsc-125)/ship.LBP)

    Pw = [0,0]
    args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
            (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    
    if stiff_plate.tag != 5: # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            for i in range(len(Pw)):
                hw  = Phs(Tlc,args[i][1])/rho/G
                if args[i][0] < Tlc :            
                    Pw[i] = max(-1*Phs(*args[i]),hydrostatic_pressure(args[i][0],Tlc,rho))
                elif args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = -1*hw*rho*G - hydrostatic_pressure(args[i][0],Tlc,rho)
                else:
                    Pw[i]=0
        else:
            for i in range(len(Pw)):
                hw  = Phs(Tlc,args[i][1])/rho/G
                if args[i][0] < Tlc :            
                    Pw[i] = max(Phs(*args[i]),hydrostatic_pressure(args[i][0],Tlc,rho))
                elif args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = Phs(Tlc,args[i][1]) - hydrostatic_pressure(args[i][0],Tlc,rho)
                else:
                    Pw[i]=0
    elif stiff_plate.tag == 5:
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if ship.LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*ship.LBP

        hw  = Phs(Tlc,args[i][1])/rho/G
        if _1_:
            for i in range(len(Pw)):
                if args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = -1*hw*rho*G - hydrostatic_pressure(args[i][0],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
        else:
            for i in range(len(Pw)):
                if args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = Phs(Tlc,args[i][1]) - hydrostatic_pressure(args[i][0],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
        
        Pw[0] *= x
        Pw[1] *= x


    return Pw

def BSP_wave_pressure(_1_:bool,Tlc:float,rho:float,ship:cls.ship,stiff_plate:cls.stiff_plate,Port=True):
    '''
    Calculates the wave pressure over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the BSP-1 or BSP-2, taking the values True and False respectively
    Port -> indicates whether we are working on the Port or Starboard side, taking the values True and False respectively
    '''
    fnl = 0.8 # @50% Lbp pp 202
    
    fxL, fps, fbeta, ft = external_loadsC(Tlc,ship,'BSP')
    

    l = 0.2*(1+2*ft)*ship.LBP
    
    fyB = lambda x : 2*x/ship.B
    # for the time being it can be left like this as a symmetrical case focused on Port
    if Port:
        fyz = lambda x,y : 2*x/Tlc+2.5*fyB(y)+0.5 #worst case scenario 
    else:
        pass
        
    Pbsp = lambda x,y : 4.5*fbeta*fps*fnl*fyz(x,y)*ship.Cw*math.sqrt((l+ship.Lsc-125)/ship.LBP)

    Pw = [0,0]
    args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
            (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    if stiff_plate.tag != 5:
        if _1_:
            for i in range(len(Pw)):
                hw  = Pbsp(Tlc,args[i][1])/rho/G
                if args[i][0] < Tlc :            
                    Pw[i] = max(-1*Pbsp(*args[i]),hydrostatic_pressure(args[i][0],Tlc,rho/G))
                elif args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = -1*hw*rho*G - hydrostatic_pressure(args[i][0],Tlc,rho/G)
                else:
                    Pw[i]=0
        else:
            for i in range(len(Pw)):
                hw  = Pbsp(Tlc,args[i][1])/rho/G
                if args[i][0] < Tlc :            
                    Pw[i] = max(Pbsp(*args[i]),hydrostatic_pressure(args[i][0],Tlc,rho))
                elif args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = Pbsp(Tlc,args[i][1]) - hydrostatic_pressure(args[i][0],Tlc,rho)
                else:
                    Pw[i]=0
    elif stiff_plate.tag == 5:
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if ship.LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*ship.LBP

        hw  = Pbsp(Tlc,args[i][1])/rho/G
        if _1_:
            for i in range(len(Pw)):
                if args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = -1*hw*rho*G - hydrostatic_pressure(args[i][0],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
        else:
            for i in range(len(Pw)):
                if args[i][0] >= Tlc and args[i][0] < Tlc+hw:
                    Pw[i] = Pbsp(Tlc,args[i][1]) - hydrostatic_pressure(args[i][0],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0

    return Pw

