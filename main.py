# -_-
# Mpas kai teleiwsei to mpourdelo 
# #################################
'''
Structural Calculator for Bulk Carriers 
Courtesy of iwannakillmeself and kys

STUDIES HSM and BSP conditions at midships
'''
# #################################
#_____ IMPORTS _____
# import ezdxf #to be installed 
import matplotlib.pyplot as plt
import numpy as np 

#_____ CALLS _______
import modules.classes as cl
from modules.constants import RHO_S
import modules.physics as phzx
import modules.rules as csr
import modules.render as rnr
import modules.IO as IO
from modules.utilities import c_info,_TITLE_,_RESET_


def main():
    print("-"*40)
    print(_TITLE_+" ____  ____    _      __  __ ____  ____\n/ ___||  _ \  / \    |  \/  / ___||  _ \\\n\___ \| | | |/ _ \   | |\/| \___ \| | | |\n ___) | |_| / ___ \  | |  | |___) | |_| |\n|____/|____/_/   \_\ |_|  |_|____/|____/ "+_RESET_)
    print("-"*40)
    print("This code is developed to aid the design of the principal strength members of a ship's Midship. For the time being is developed for Bulk Carriers, under Common Structural Rules 2022 Version.")

    #import geometry data
    file_path = "test.json"
    ship  = IO.load_ship(file_path)
    #calculate pressure distribution
    phzx.Static_total_eval(ship,16,RHO_S,False)
    HSM1,HSM2 = phzx.Dynamic_total_eval(ship,16,'HSM',False)
    BSP1,BSP2 = phzx.Dynamic_total_eval(ship,16,'BSP',False)
    # rnr.pressure_plot(ship,'HSM-1','DC')
    # rnr.pressure_plot(ship,'STATIC','DC')
    # rnr.block_plot(ship)
    # rnr.pressure_plot(ship,'Null','SEA',True)
    # rnr.pressure_plot(ship,'HSM-2','DC')
    # rnr.pressure_plot(ship,'BSP-1P','DC')
    # rnr.pressure_plot(ship,'BSP-2P','DC')
    #calculation Recipes
    FLC =  {
        'Dynamics':'S+D',
        'max value': 'DC',
        'skip value':'LC,WB,OIL,FW,VOID'
    }
    WB =  {
        'Dynamics':'S+D',
        'max value': '',
        'skip value':'DC,LC,OIL,FW,VOID'
    }
    for case in (HSM1,HSM2,BSP1,BSP2):
        csr.Loading_cases_eval(ship,case,FLC)
        csr.Loading_cases_eval(ship,case,WB)

    IO.ship_save(ship,'out.json')


main()