"""
This module provides the functions that calculate the pressures applied on the plates
"""
from utilities import c_error,c_warn
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

def wave_pressure(z:float,T:float,rho:float):


