# Constructional Strength Calculations
This was part of a ship design assignment, by [SNAME @ NTUA](http://www.naval.ntua.gr/).

## Primary goal
This code is developed to aid the design of the principal strength members of a ship's Midship.
For the time being is developed for Bulk Carriers, under Common Structural Rules.

## Installation
Python3.9 or later **REQUIRED**!

```bash
git clone git@github.com:KonstantinosRekoumis/CSR.git && cd CSR
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Running

[//]: # ( add instructions on how to run the terminal version, and the gui version )
- cli version:
    1. Open the `cli.py` with your favorite text editor and navigate to the bottom of the file
    2. There change the path of the envelope's json file to the path of the your project's .json file
    4. Run the `cli.py` with the CSR python environment activated
- gui version:
    1. Run the `gui.py` with the CSR python environment activated

## Design Comments on the Ordinary Section

- The Weather Deck is thicker than calculated to get a boost in Z,deck (also we done no calculations for the hatch coamings)
- The Weather Deck stiffeners are essentially ` impostor ` bulbous stiffeners
- The Inner Bottom and Bottom Shell plates are roughly the same size for construction homogeneity 
- The wing tank makes sense to have multiple plates like in the mother ship though design is kept simple for the time being.
- The plates where given dimensions based on the mother ship without following them to heart
- The plates may be thicker than the calculations imply but this is done to ensure we have adequate area moments

## Goals

- [x] Finish CSR for thesis
- [x] Add functions to export calculation data to a reportable form (copium) (base is probably done, need to actually use and grab function values)
- [x] PSM spacing per plate to account for Bulk Carriers (reasonable)
- [x] Add info about the null corrosion check done for girders
- [X] Fix Z calculation for stiffener
- [x] Add t_net calculated
- [x] Girder LaTeX fix for Corrosion thickness
- [x] Add info about the null corrosion check done for girders
- [x] Fix the input file for the Tmin, Lsc and Tsc  
- [x] Account for symmetry  
- [x] Add I calculation for symmetrical sections 
- [x] State the axis convention(done the graphical important thing)
- [x] Include the girders in the calculations 
- [x] **Include null plates to define volume without joining in the strength calculations**
- [x] Create I and Z checks
- [x] Calculate I_{y-n50} and I_{z-n50} (with corrosion addition) 
- [x] FIX FOR STATIC LOADS AT PLATING AND STIFFENER SCANTLING (not sloshing bs)
- [x] Check special plating cases -> side shell (ez) -> Bilge plates(medium) Bilge plate needs to have as paddings the neighboring plates' inverse paddings
- [x] Program T beams for stiffeners 
- [x] IMPLEMENT BUCKLING STRENGTH CHECK -> Implement shear beam reduction (check for total Moment of Inertia) Part 1 Chapter 8 Section 2  
- [x] **Finalize the Section Modelling**
- [x] Create exception for fender contact zone
- [x] Modify the corrosion addition function to account for 0 state entry ( all thicknesses are less than corrosion addition)  
- [x] **ESSAY -> Change the table figures, iamges, check for mistakes, add beff in Inertia Calculations**
- [x] Close the LaTeX export (check the savefig func)
- [ ] Not lose sanity
- [x] physics module HSM ans BSP need Lwl not LBP on weather deck calculations (actually they needed Lsc) 
- [x] Fix colorbar, added multiple subplots 
- [x] kr and GM calculation is different for WB, add to `__init__()` (actually use it)

## Future Extensions

- [x] Augment the physics external_loadC method to account for more cases (only fully supports HSM and BSP) ( PhysicsData class fixed the is sue) 
- [ ] Augment rules to automatically check if a plate's material is of correct class
- [ ] Play with colormaps in contour plots 
- [ ] Improve documentation 

## LICENSE
MIT License

Copyright (c) 2022 Konstantinos Rekoumis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
