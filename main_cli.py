# -_-
# #################################
"""
Structural Calculator for Bulk Carriers
Courtesy of Navarx0s and his st0los

STUDIES HSM and BSP conditions at midships
"""
# #################################
# _____ IMPORTS _____
# import ezdxf #to be installed 

# _____ CALLS _______
import os

import modules.datahandling.IO as IO
from modules.datahandling.datalogger import DataLogger
from modules.datahandling.latex import generate_latex_rep
import modules.physics.physics as phzx
import modules.render as rnr
import modules.rules as csr
from modules.constants import RHO_S
from modules.utilities import c_info, c_success


def main(filepath, ship_plots, pressure_plots):
    title = r"""
       ____  ____    _      __  __ ____  ____    
      / ___||  _ \  / \    |  \/  / ___||  _ \\  
      \___ \| | | |/ _ \   | |\/| \___ \| | | |  
       ___) | |_| / ___ \  | |  | |___) | |_| |  
      |____/|____/_/   \_\ |_|  |_|____/|____/   
    --- SHIP DESIGN ASSIGNMENT MIDSHIP DESIGN ---
        ---- 2022, Rekoumis Konstantinos ----    
      ### All Rights Reserved - MIT License ###  
    This code is developed to aid the design of the 
    principal strength members of a ship\'s Midship. 
    For the time being is developed for Bulk Carriers,
    under Common Structural Rules 2022 Version.
    """
    print(title)
    # import geometry data
    ship = IO.load_ship(filepath)
    logger = DataLogger(ship)
    logger.LoadData()
    c_info(f'# => The ship at location {filepath} has been successfully loaded.')
    if ship_plots:
        rnr.lines_plot(ship)
        for i in ('id', 'tag', 'thickness', 'material'):
            rnr.contour_plot(ship, key=i)
        rnr.block_plot(ship)
    # calculate pressure distribution
    c_info('# => Evaluating Corrosion Reduction for stiffened plates...', default=False)
    csr.corrosion_assign(ship, offload=True)
    c_info('# => Proceeding to calculating the Specified Static and Dynamic Cases..', default=False)
    phzx.static_total_eval(ship, 16, RHO_S, False)
    hsm1, hsm2 = phzx.dynamic_total_eval(ship, 16, 'HSM', False)
    bsp1, bsp2 = phzx.dynamic_total_eval(ship, 16, 'BSP', False)
    logger.LoadConds([x.cond for x in (hsm1, hsm2, bsp1, bsp2)])
    if pressure_plots:
        rnr.pressure_plot(ship, 'HSM-1', 'SEA,ATM', path='./essay/HSM1_Shell.pdf')
        rnr.pressure_plot(ship, 'STATIC', 'SEA,ATM', path='./essay/STATIC_Shell.pdf')
        rnr.pressure_plot(ship, 'Normals', 'SEA', True, path='./essay/NORMALS.png')
        rnr.pressure_plot(ship, 'HSM-2', 'SEA,ATM', path='./essay/HSM2_Shell.pdf')
        rnr.pressure_plot(ship, 'BSP-1P', 'SEA,ATM', path='./essay/BSP1_Shell.pdf')
        rnr.pressure_plot(ship, 'BSP-2P', 'SEA,ATM', path='./essay/BSP2_Shell.pdf')

    c_info('# => Evaluating Stiffened Plates Slenderness Requirements...')
    ship.evaluate_beff()
    csr.buckling_evaluator(ship, debug=False)
    c_info('# => Static and Dynamic cases successfully evaluated. Proceeding to plating calculations..', default=False)
    # calculation Recipes
    flc = {
        'Dynamics': 'S+D',
        'max value': 'DC',
        'skip value': 'LC,WB,OIL,FW,VOID'
    }
    wb = {
        'Dynamics': 'S+D',
        'max value': '',
        'skip value': 'DC,LC,OIL,FW,VOID'
    }

    c_info(f'#=> Evaluating Full Load Condition...')
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.loading_cases_eval(ship, case, flc, logger)
    c_info('# => Pressure offloading to plates concluded. Evaluating plating thickness...', default=False)
    c_info('# => Evaluating Local Scantlings of stiffened plates...', default=False)
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.net_scantling(ship, case, flc['Dynamics'], debug=False)

    c_info(f'#=> Evaluating Water Ballast Condition...')
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.loading_cases_eval(ship, case, wb, logger)
    c_info('# => Pressure offloading to plates concluded. Evaluating plating thickness...', default=False)
    c_info('# => Evaluating Local Scantlings of stiffened plates...', default=False)
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.net_scantling(ship, case, wb['Dynamics'], debug=False)

    c_info('# => Evaluating the Sections Moments and Checking with the Rules...')
    csr.ship_scantlings(ship)
    c_info('# => Evaluating Corrosion Addition for stiffened plates...', default=False)
    csr.corrosion_assign(ship, offload=False)

    if ship_plots:
        for i in ('tag', 'thickness'):
            rnr.contour_plot(ship, key=i)

    c_info('# => Outputing Data to /out.json file...', default=False)
    IO.ship_save(ship, 'out.json')
    c_info('# => Generating LaTeX Report Data to /out.json file...', default=False)
    generate_latex_rep(logger, path='./essay/', _standalone=False)
    c_success('Program terminated succesfully!')


if __name__ == "__main__":
    # Three step automated design method 
    auto = False
    if auto:
        main('./in.json', False, False)
        main('./out.json', False, False)
    # Single Step Manual Design evaluation
    else:
        # main('./structural-out/final.json', True, True)
        main('./structural-out/final.json', False, False)