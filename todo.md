# To Do 

## Major Importance

1) Do the project
1) Fix the input file for the Tmin, Lsc and Tsc  [x]
1) Account for symmetry [x] 
1) Add I calculation for symmetrical sections [x]
1) State the axis convention
1) Include the girders in the calculations
1) Include null plates to define volume without joining in the strength calculations
1) Create I and Z checks
1) Calculate I_{y-n50} and I_{z-n50} (with corrosion addition) [x]
1) FIX FOR STATIC LOADS AT PLATING AND STIFFENER SCANTLING (not sloshing bs)
1) Check special plating cases -> side shell (ez) -> Bilge plates(medium)[x] Bilge plate needs to have as paddings the neighboring plates' inverse paddings
1) Program T beams for stiffeners [x]
1) IMPLEMENT BUCKLING STRENGTH CHECK -> Implement shear beam reduction (check for total Moment of Inertia) Part 1 Chapter 8 Section 2 [x]
1) Finalize the Section Modelling
1) Create exception for fender contact zone
1) Modify the corrosion addition function to account for 0 state entry ( all thicknesses are less than corrosion addition) [x]
1) ESSAY -> Change the table figures
## Medium Importance

1) Not lose sanity  
1) physics module HSM ans BSP need Lwl not LBP on weather deck calculations (actually they needed Lsc) [x]
1) Fix colorbar, added multiple subplots [x]
1) kr and GM calculation is different for WB, add to __init__()[x] (actually use it)

## Minor Importance - Future Extending

1) Augment the physics external_loadC method to account for more cases (only fully supports HSM and BSP) ( PhysicsData class fixed the issue) [x]
1) Augment rules to automatically check if a plate's material is of correct class