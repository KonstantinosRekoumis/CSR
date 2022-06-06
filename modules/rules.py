# #############################
# CSR Rules and Regulations for Dry Cargo
# #############################

#Materials Constant Array see. CSR ... to be filled
import classes as cls



MATERIALS = {
    "A" : 235,
    "AH32" : 315,
    'AH36' : 355,
    'AH40' : 390

}
# # {'Reh' : 235, 'Rm' : 400}
# def scantling_req(st_plate : stif_plate, ship : ship) :

def net_scantling(plate : cls.plate):
    return 0

def gross_scantling(plate: cls.plate):
    # CSR Chapter 1 Section 3
    Corr = {
        "WBT": {
            "FacePlate":{
                "=< 3,tank_top" : 2.0,
                "else":1.5},
            "OtherMembers":{
                "=< 3,tank_top" : 2.0,
                "else":1.5}
            },
        "CHP": {
            "UpperPart" : 1.8,
            "Hopper/InBot": 3.7
        },
        "X2A": {
            "WeatherDeck": 1.7,
            "Other":1.0
        },
        "X2SW":{
            "Wet/Dried": 1.5,
            "Wet": 1.0
        },
        "Misc":{
            "FO/FW/LO/VS":0.7,
            "DrySpace":0.5
        }

    }
    plate.thickness = net_scantling(plate) + t_corr