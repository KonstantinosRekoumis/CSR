'''
----------------------------------------------------\n
                    Constants.py\n
An auxiliary file holding various GLOBAL CONSTANTS\n
that would be troublesome and tedious to manually \n
include in each source code file.\n
!!!!!---ONLY TO DECLARE GLOBAL PUBLIC VARIABLES---!!! \n
!! DONT USE AS A CROUCH TO CREATE CASE SPECIFIC CODE !!\n
----------------------------------------------------
'''
#____ CONSTANTS ________
RHO_S = 1.025 # tn/m^3 sea water @ 17 Celsius
RHO_F = 0.997 # tn/m^3 fresh water @ 17 Celsius
G = 9.8063 # gravitational acceleration

HEAVY_HOMO = 0.8

LOADS = {
    #Block TAG : {Content Properties}
    'WB' : {'rho':RHO_S,'hair':0.0},
    'DC' : {'rho':HEAVY_HOMO,'fdc':1.0,'psi':30},
    'LC' : {'rho':0.8,'Ppv': 25,'fcd':1.0},
    'OIL': {'rho':0.8,'hair':0.0},
    'FW' : {'rho':RHO_F,'hair':0.0},
    'VOID':{'rho':0.0,'hair':0.0}}

STATIC = {
    'Liquids':['S-NOS','S-HSWO'],
    'Dry':'STATIC',
    'Sea':'STATIC'
}

MATERIALS = {
    "A" : {'Reh':235,'Rm':(400,520)},
    "AH32" : {'Reh':315,'Rm':(440,570)},
    'AH36' : {'Reh':355,'Rm':(490,630)},
    'AH40' : {'Reh':390,'Rm':(510,660)}

}