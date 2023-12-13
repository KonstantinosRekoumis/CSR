# -_-
# #################################
"""
Structural Calculator for Bulk Carriers
Courtesy of Navarx0s and his st0los

Studies HSM and BSP conditions at midships
"""
# #################################
# _____ IMPORTS _____
# import ezdxf #to be installed 

# _____ CALLS _______

import modules.datahandling.IO as IO
import modules.physics.physics as phzx
import modules.render as rnr
import modules.rules as csr
from modules.constants import RHO_S
from modules.datahandling.datalogger import DataLogger
from modules.datahandling.latex import generate_latex_rep
from modules.utilities import Logger


def evaluate_condition(hsm1, hsm2, bsp1, bsp2, ship, condition: dict[str, str], logger):
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.loading_cases_eval(ship, case, condition, logger)
    Logger.info(' Pressure offloading to plates concluded. Evaluating plating thickness...')
    Logger.info(' Evaluating Local Scantlings of stiffened plates...')
    for case in (hsm1, hsm2, bsp1, bsp2):
        csr.net_scantling(ship, case, condition['Dynamics'])


def main(filepath, ship_plots, pressure_plots):
    print(r"""
       ____  ____    _      __  __ ____  ____    
      / ___||  _ \  / \    |  \/  / ___||  _ \  
      \___ \| | | |/ _ \   | |\/| \___ \| | | |  
       ___) | |_| / ___ \  | |  | |___) | |_| |  
      |____/|____/_/   \_\ |_|  |_|____/|____/   
    --- SHIP DESIGN ASSIGNMENT MIDSHIP DESIGN ---
        ---- 2022, Rekoumis Konstantinos ----    
      ###           MIT License            ###  
    This code is developed to aid the design of the 
    principal strength members of a ship\'s Midship. 
    For the time being is developed for Bulk Carriers,
    under Common Structural Rules 2022 Version.
    """)

    # import geometry data
    ship = IO.load_ship(filepath)
    logger = DataLogger(ship)
    logger.LoadData()
    Logger.success(f' The ship at location {filepath} has been successfully loaded.')
    if ship_plots:
        rnr.lines_plot(ship)
        for i in ('id', 'tag', 'thickness', 'material'):
            rnr.contour_plot(ship, key=i)
        rnr.block_plot(ship)
    # calculate pressure distribution
    Logger.info(' Evaluating Corrosion Reduction for stiffened plates...')
    csr.corrosion_assign(ship, offload=True)
    Logger.info(' Proceeding to calculating the Specified Static and Dynamic Cases..')
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

    Logger.info('Evaluating Stiffened Plates Slenderness Requirements...')
    ship.evaluate_beff()
    csr.buckling_evaluator(ship)

    Logger.info('Static and Dynamic cases successfully evaluated. Proceeding to plating calculations..')
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

    Logger.info(f'Evaluating Full Load Condition...')
    evaluate_condition(hsm1, hsm2, bsp1, bsp2, ship, flc, logger)

    Logger.info(f'Evaluating Water Ballast Condition...')
    evaluate_condition(hsm1, hsm2, bsp1, bsp2, ship, wb, logger)

    Logger.info('Evaluating the Sections Moments and Checking with the Rules...')
    csr.ship_scantlings(ship)

    Logger.info('Evaluating Corrosion Addition for stiffened plates...')
    csr.corrosion_assign(ship, offload=False)

    if ship_plots:
        for i in ('tag', 'thickness'):
            rnr.contour_plot(ship, key=i)

    Logger.info('Outputting Data to /out.json file...')
    IO.ship_save(ship, 'out.json')
    Logger.info('Generating LaTeX Report Data to /out.json file...')
    generate_latex_rep(logger, path='./essay/', _standalone=False)
    Logger.success('Program terminated successfully!')


if __name__ == "__main__":
    # Three step automated design method 
    auto = False
    if auto:
        main('./in.json', False, False)
        main('./out.json', False, False)
    # Single Step Manual Design evaluation
    else:
        main('./structural-out/final.json', True, True)
        Logger.info('Initial pass evaluated results successfully. Renaming ./out.json to ./inter.json.')