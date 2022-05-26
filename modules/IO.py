import classes as cls
import json

def file_load(filename : str,):
    with open(filename,'r') as file:
        text=file.read()

    data = json.loads(text)
    return data

def plate_save(plate:cls.plate):
    # Save data to JSON format
    return json.dumps([plate.start,plate.end,plate.thickness,plate.material])

def stiff_save(stiff:cls.stiffener):
    # Save data to JSON format
    dim = []
    for i in stiff.plates:
        dim.append(i.length)
        dim.append(i.thickness)

    return json.dumps({'type': stiff.type,'dimensions':dim})

def stiff_pl_save(stiff_plate:cls.stiff_plate):
    save = ""
    save += '{\'plate\':'+plate_save(stiff_plate.plate)+","
    save += '\'stiffener\':'+stiff_save(stiff_plate.stiffeners[0])+","
    save += '\'spacing\':'+json.dumps(stiff_plate.spacing*1e3)+"}"

    return save

def section_save(ship:cls.ship):
    save = '\'geometry\':[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i)+',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'

    return save

def ship_save(ship:cls.ship,filename:str):
    save = "{\'LBP\':"+str(ship.LBP)+',\n'
    save += "\'B\':"+str(ship.B)+',\n'
    save += "\'T\':"+str(ship.T)+',\n'
    save += "\'D\':"+str(ship.D)+',\n'
    save += "\'Cb\':"+str(ship.Cb)+',\n'
    save += "\'Cp\':"+str(ship.Cp)+',\n'
    save += "\'Cm\':"+str(ship.Cm)+',\n'
    save += "\'DWT\':"+str(ship.DWT)+',\n'

    save += section_save(ship)

    with open(filename,'w') as file:
        file.write(save)


def load_stiff(data):
    # if stiff.type == 'fb' or stiff.type == 'bb':
    #     dim = [stiff.plates[0].length,stiff.plates[0].thickness]
    # elif stiff.type == 'g' or stiff.type == 't':
    #     dim = [stiff.plates[0].length,stiff.plates[0].thickness]
    return 0