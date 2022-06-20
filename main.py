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
import ezdxf #to be installed 
import matplotlib.pyplot as plt
import numpy as np 

#_____ CALLS _______
import modules.classes as cl
import modules.rules as csr
import modules.render as rd
import modules.IO as IO


def main():
    #import geometry data
    file_path = "test.json"
    ship  = IO.load_ship(file_path)
