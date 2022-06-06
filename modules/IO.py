import classes as cls
import json



def plate_save(plate:cls.plate):
    # Save data to JSON format
    return json.dumps([plate.start,plate.end,plate.thickness,plate.material,plate.tag])

def stiff_save(stiff:cls.stiffener):
    # Save data to JSON format
    dim = []
    for i in stiff.plates:
        dim.append(i.length*1e3)
        dim.append(i.thickness*1e3)

    return json.dumps({'type': stiff.type,'dimensions':dim,'material':stiff.plates[0].material})

def stiff_pl_save(stiff_plate:cls.stiff_plate):
    save = ""
    save += '{\"plate\":'+plate_save(stiff_plate.plate)+","
    save += '\"stiffeners\":'+stiff_save(stiff_plate.stiffeners[0])+","
    save += '\"spacing\":'+json.dumps(stiff_plate.spacing*1e3)+"}"

    return save

def section_save(ship:cls.ship):
    save = '\"geometry\":[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i)+',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'

    return save

def ship_save(ship:cls.ship,filename:str):
    save = "{\"LBP\":"+str(ship.LBP)+',\n'
    save += "\"B\":"+str(ship.B)+',\n'
    save += "\"T\":"+str(ship.T)+',\n'
    save += "\"D\":"+str(ship.D)+',\n'
    save += "\"Cb\":"+str(ship.Cb)+',\n'
    save += "\"Cp\":"+str(ship.Cp)+',\n'
    save += "\"Cm\":"+str(ship.Cm)+',\n'
    save += "\"DWT\":"+str(ship.DWT)+',\n'

    save += section_save(ship) +"\n}"

    with open(filename,'w') as file:
        file.write(save)


def load_ship(filename):
    with open(filename,'r') as file:
        data = json.loads(file.read())

    LBP = data['LBP']
    B  = data['B']
    T = data['T']
    D = data['D']
    Cb = data['Cb']
    Cp = data['Cp']
    Cm = data['Cm']
    DWT = data['DWT']
    stiff_plates = geometry_parser(data['geometry'])

    if len(stiff_plates)  != 0:
        return cls.ship( LBP, B, T, D, Cb, Cp, Cm, DWT, stiff_plates)
    else:
        print("Check your input file")
        quit()

    
def geometry_parser(geo_t:list):
    out = []
    for i in geo_t:
        # i['plate'] = [start,end,thickness,material,tag]
        # stiffener_dict = {type : str, dims : [float],mat:str}
        try:
            if len(i['plate'] )== 5:
                tmp_p = cls.plate(i['plate'][0],i['plate'][1],i['plate'][2],i['plate'][3],i['plate'][4])
                tmp_d = i['stiffeners']["dimensions"]
                if len(tmp_d)==2 and i['stiffeners']["type"] == 'fb':
                    dims = {'lw':tmp_d[0],'bw':tmp_d[1]}
                elif len(tmp_d)==4 and i['stiffeners']["type"] == 'g':
                    dims = {'lw':tmp_d[0],'bw':tmp_d[1],'lf':tmp_d[2],'bf':tmp_d[3]}
                else: 
                    print("You input a stiffener type that has less dims than needed")
                    continue
                tmp_s = {'type':i['stiffeners']['type'],'material':i['stiffeners']['material'],'dimensions': dims}
                tmp = cls.stiff_plate(tmp_p,i['spacing'],tmp_s)
                out.append(tmp)
            else:
                print(f"Loading stiffened plate {i} has resulted in an error. Thus the code will ignore its existence.")
        except KeyboardInterrupt:
            print(f"KeyError: Loading stiffened plate {i} has resulted in an error. Thus the code will ignore its existence.")
    
    return out