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
import modules.rules as csr
import modules.render as rd
import modules.IO as IO
from modules.utilities import c_info,_TITLE_,_RESET_


def main():
    print("-"*40)
    print(_TITLE_+" ____  ____    _      __  __ ____  ____\n/ ___||  _ \  / \    |  \/  / ___||  _ \\\n\___ \| | | |/ _ \   | |\/| \___ \| | | |\n ___) | |_| / ___ \  | |  | |___) | |_| |\n|____/|____/_/   \_\ |_|  |_|____/|____/ "+_RESET_)
    print("-"*40)
    print("This code is developed to aid the design of the principal strength members of a ship's Midship. For the time being is developed for Bulk Carriers, under Common Structural Rules.")

    #import geometry data
    file_path = "test.json"
    ship  = IO.load_ship(file_path)

    #calculation Recipes

    FLD_SEA_HOG = {
        "Primary": ship.Msw_h_mid,
        "External": True,
        # "Internal": 
    }

    FLD_HBR_HOG = {
        "Primary": ship.Mwh,
        "External": True,
        # "Internal":
    }

main()