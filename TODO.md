# To Do 

## Major Importance

- [ ] Do the project
- [x] Fix the input file for the Tmin, Lsc and Tsc  
- [x] Account for symmetry  
- [x] Add I calculation for symmetrical sections 
- [x] State the axis convention(done the graphical important thing)
- [ ] Include the girders in the calculations
- [x] **Include null plates to define volume without joining in the strength calculations**
- [x] Create I and Z checks
- [x] Calculate I_{y-n50} and I_{z-n50} (with corrosion addition) 
- [x] FIX FOR STATIC LOADS AT PLATING AND STIFFENER SCANTLING (not sloshing bs)
- [x] Check special plating cases -> side shell (ez) -> Bilge plates(medium) Bilge plate needs to have as paddings the neighboring plates' inverse paddings
- [x] Program T beams for stiffeners 
- [x] IMPLEMENT BUCKLING STRENGTH CHECK -> Implement shear beam reduction (check for total Moment of Inertia) Part 1 Chapter 8 Section 2  
- [ ] **Finalize the Section Modelling**
- [x] Create exception for fender contact zone
- [x] Modify the corrosion addition function to account for 0 state entry ( all thicknesses are less than corrosion addition)  
- [ ] **ESSAY -> Change the table figures, iamges, check for mistakes**
- [x] Close the LaTeX export (check the savefig func)

## Medium Importance

1) [ ] Not lose sanity 
1) [ ] Documentation of Code is bare minimum ; add stuff 
1) [x] physics module HSM ans BSP need Lwl not LBP on weather deck calculations (actually they needed Lsc) 
1) [x] Fix colorbar, added multiple subplots 
1) [x] kr and GM calculation is different for WB, add to __init__() (actually use it)

## Minor Importance - Future Extending

1) [x] Augment the physics external_loadC method to account for more cases (only fully supports HSM and BSP) ( PhysicsData class fixed the is sue) 
1) [ ] Augment rules to automatically check if a plate's material is of correct class
1) [ ] Play with colormaps in contour plots 