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
from modules.utilities import c_info,_TITLE_,_RESET_, c_success


def main(filepath,SHIP_PLOTS,PRESSURE_PLOTS):
    print("-"*45)
    print(_TITLE_+" ____  ____    _      __  __ ____  ____\n/ ___||  _ \  / \    |  \/  / ___||  _ \\\n\___ \| | | |/ _ \   | |\/| \___ \| | | |\n ___) | |_| / ___ \  | |  | |___) | |_| |\n|____/|____/_/   \_\ |_|  |_|____/|____/ "+_RESET_)
    print("-"*45)
    print('--- SHIP DESIGN ASSIGNMENT MIDSHIP DESIGN ---')
    print('    ---- 2022, Rekoumis Konstantinos ----')
    print("This code is developed to aid the design of the principal strength members of a ship's Midship. For the time being is developed for Bulk Carriers, under Common Structural Rules 2022 Version.")

    #import geometry data
    ship  = IO.load_ship(filepath)
    c_info(f'# => The ship at location {filepath} has been successfully loaded.')
    if SHIP_PLOTS:
        ship.render()
        for i in ('id','tag','thickness','material'):
            rnr.contour_plot(ship,key=i)
        rnr.block_plot(ship)
    #calculate pressure distribution
    c_info('# => Evaluating Corrosion Reduction for stiffened plates...',default= False)
    csr.corrosion_assign(ship,input=True)
    c_info('# => Proceeding to calculating the Specified Static and Dynamic Cases..',default=False)
    phzx.Static_total_eval(ship,16,RHO_S,False)
    HSM1,HSM2 = phzx.Dynamic_total_eval(ship,16,'HSM',False)
    BSP1,BSP2 = phzx.Dynamic_total_eval(ship,16,'BSP',False)
    if PRESSURE_PLOTS:
        rnr.pressure_plot(ship,'HSM-1','SEA,ATM')
        rnr.pressure_plot(ship,'STATIC','SEA,ATM')
        rnr.pressure_plot(ship,'Normals','WB',True)
        rnr.pressure_plot(ship,'HSM-2','SEA,ATM')
        rnr.pressure_plot(ship,'BSP-1P','SEA,ATM')
        rnr.pressure_plot(ship,'BSP-2P','SEA,ATM')

    c_info('# => Static and Dynamic cases successfully evaluated. Proceeding to plating calculations..',default=False)
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

    c_info(f'#=> Evaluating Full Load Condition...')
    for case in (HSM1,HSM2,BSP1,BSP2):
        # rnr.pressure_plot(ship,case.cond,'DC')
        csr.Loading_cases_eval(ship,case,FLC)
    c_info('# => Pressure offloading to plates concluded. Evaluating plating thickness...',default=False)
    c_info('# => Evaluating Local Scantlings of stiffened plates...',default= False)
    for case in (HSM1,HSM2,BSP1,BSP2):
        csr.net_scantling(ship,case,Debug=False)
    # csr.net_scantling(ship,HSM1,Debug=False)

    c_info(f'#=> Evaluating Water Ballast Condition...')
    for case in (HSM1,HSM2,BSP1,BSP2):
        csr.Loading_cases_eval(ship,case,WB)
    c_info('# => Pressure offloading to plates concluded. Evaluating plating thickness...',default=False)
    c_info('# => Evaluating Local Scantlings of stiffened plates...',default= False)
    for case in (HSM1,HSM2,BSP1,BSP2):
        csr.net_scantling(ship,case,Debug=False)
    c_info('# => Evaluating Sitffened Plates Slenderness Requirements...')
    csr.buckling_evaluator(ship,Debug=False)
    c_info('# => Evaluating the Sections Moments and Checking with the Rules...')
    csr.ship_scantlings(ship)
    c_info('# => Evaluating Corrosion Addition for stiffened plates...',default= False)
    csr.corrosion_assign(ship,input=False)

    if SHIP_PLOTS:
        for i in ('tag','thickness'):
            rnr.contour_plot(ship,key=i)

    c_info('# => Outputing Data to /out.json file...',default= False)
    IO.ship_save(ship,'out.json')
    c_success('Program terminated succesfully!')


if __name__ == "__main__":
    # main(True,True)
    main('./in.json',False,False)
    main('./out.json',False,False)
    main('./out.json',False,False)
    