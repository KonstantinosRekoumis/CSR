# #############################
# CSR Rules and Regulations for Dry Cargo
# #############################

#Materials Constant Array see. CSR ... to be filled
import classes as cls

# page 378 the application table

MATERIALS = {
    "A" : 235,
    "AH32" : 315,
    'AH36' : 355,
    'AH40' : 390

}
# # {'Reh' : 235, 'Rm' : 400}
# def scantling_req(st_plate : stiff_plate, ship : ship) :

def net_scantling(plate : cls.plate):
    return 0

def corrosion_addition(stiff_plate: cls.stiff_plate, blocks : list[cls.block], Tmin, Tmax  ):
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
    #Grab tags
    tags = []
    for i in blocks:
        if stiff_plate.id in i.list_plates_id:
            tags.append(i.space_type)

    if stiff_plate.tag in (0,4): #Shell plates
        Y = max(stiff_plate.plate.start[1],stiff_plate.plate.end[1])
        if Y <= Tmin:
            plate_t_corr = Corr['X2SW']['Wet']
        elif Y > Tmin and Y < Tmax:
            plate_t_corr = Corr['X2SW']['Wet/Dried']
        elif Y > Tmax :
            plate_t_corr = Corr['X2A']['WeatherDeck'] #Is it tho ?

        t_in = 0
        for i in tags:
            if "WB" == i :
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top'] : t_in = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"] : t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"] : t_in = Corr["Misc"]["DrySpace"]
        
        plate_t_corr += t_in

    elif stiff_plate.tag in (1,2,3): #Inner Bottom, Hopper, Wing
        t= (0,0)
        ind = 0
        c = 0 
        while c <= 1: #not the best way but oh well
            for tag,i in enumerate(tags):
                if "WB" == tag :
                    if t[c] < Corr['WBT']['FacePlate']['=< 3,tank_top'] : 
                        t[c] = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
                        ind = i
                elif 'DC' == tag:
                    if t[c] < Corr["CHP"]["UpperPart"]:
                        t[c] = Corr["CHP"]["UpperPart"]
                        ind = i
                elif 'OIL' == tag or 'FW' == tag:
                    if t[c] < Corr["Misc"]["FO/FW/LO/VS"] : 
                        t[c] = Corr["Misc"]["FO/FW/LO/VS"]
                        ind = i
                elif 'VOID' == tag:
                    if t[c] < Corr["Misc"]["DrySpace"] : 
                        t[c] = Corr["Misc"]["DrySpace"]
                        ind = i
            tags.pop(ind)
            c+=1
        plate_t_corr = t[0]+t[1]

    elif stiff_plate.tag == 5: #Weather Deck
        plate_t_corr = Corr["X2A"]["WeatherDeck"]
        t_in = 0
        for i in tags:
            if "WB" == i :
                if t_in < Corr['WBT']['FacePlate']['=< 3,tank_top'] : t_in = Corr['WBT']['FacePlate']['=< 3,tank_top'] 
            elif 'DC' == i:
                if t_in < Corr["CHP"]["UpperPart"]: t_in = Corr["CHP"]["UpperPart"]
            elif 'OIL' == i or 'FW' == i:
                if t_in < Corr["Misc"]["FO/FW/LO/VS"] : t_in = Corr["Misc"]["FO/FW/LO/VS"]
            elif 'VOID' == i:
                if t_in < Corr["Misc"]["DrySpace"] : t_in = Corr["Misc"]["DrySpace"]

        plate_t_corr += t_in
    return  plate_t_corr





