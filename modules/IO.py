from utilities import _ERROR_,_RESET_,_WARNING_,c_error,c_warn
import classes as cls
import json



def plate_save(plate:cls.plate):
    # Save data to JSON format
    return json.dumps(plate.save_data())

def stiff_save(stiff:cls.stiffener):
    # Save data to JSON format
    dim = []
    for i in stiff.plates:
        dim.append(i.length*1e3)
        dim.append(i.thickness*1e3)

    return json.dumps({'type': stiff.type,'dimensions':dim,'material':stiff.plates[0].material})

def stiff_pl_save(stiff_plate:cls.stiff_plate):
    save = ""
    save += '{\"id\":'+str(stiff_plate.id)+',\"plate\":'+plate_save(stiff_plate.plate)+","
    if len(stiff_plate.stiffeners) != 0:
        save += '\"stiffeners\":'+stiff_save(stiff_plate.stiffeners[0])+","
    save += '\"spacing\":'+json.dumps(stiff_plate.spacing*1e3)+","
    save += '\"skip\":'+json.dumps(stiff_plate.skip)+","
    save += '\"l_pad\":'+json.dumps(stiff_plate.l_pad*1e3)+","
    save += '\"r_pad\":'+json.dumps(stiff_plate.r_pad*1e3)+"}"
    return save

def blocks_save(block:cls.block):
    save =""
    save += "{\"type\":\""+block.space_type+"\",\"ids\":"+json.dumps(block.list_plates_id)+"}"
    return save

def section_save(ship:cls.ship):
    save = '\"geometry\":[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i)+',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'
    #Added Blocks feature
    save += ',\n\"blocks\":[\n'
    for i in ship.blocks:
        save += blocks_save(i)+',\n'
    save = save[:-2] + '\n]'

    return save

def ship_save(ship:cls.ship,filename:str):
    save = "{\"LBP\":"+str(ship.LBP)+',\n'
    save += "\"Lsc\":"+str(ship.Lsc)+',\n'
    save += "\"B\":"+str(ship.B)+',\n'
    save += "\"T\":"+str(ship.T)+',\n'
    save += "\"Tmin\":"+str(ship.Tmin)+',\n'
    save += "\"Tsc\":"+str(ship.Tsc)+',\n'
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
    tags = ['LBP','Lsc','B','T','Tmin','Tsc','D','Cb','Cp','Cm','DWT']
    particulars = []
    for i in tags:
        try:
            particulars.append(data[i])
        except KeyError:
            print(_ERROR_,f"The input file is not appropriately formatted, and it is missing crucial data.\n Value: \'{i}\' is missing.",_RESET_)
            quit()
    try:
        stiff_plates = geometry_parser(data['geometry'])
        if len(stiff_plates) == 0:
            print(_ERROR_,"Check your input file",_RESET_)
            quit()
    except KeyError:
        print(_ERROR_,"The input file is not appropriately formatted, and it is missing crucial data.\n Value: 'geometry' is missing.",_RESET_)
        quit()
    try:
        blocks = blocks_parser(data['blocks'])
        if len(blocks) == 0:
            print(_ERROR_,"Check your input file",_RESET_)
            quit()
    except KeyError:
        print(_ERROR_,"The input file is not appropriately formatted, and it is missing crucial data.\n Value: 'geometry' is missing.",_RESET_)
        quit()

    return cls.ship( *particulars, stiff_plates,blocks)

    
def geometry_parser(geo_t:list):
    out = []
    temp_id = []
    for i in geo_t:
        # i['plate'] = [start,end,thickness,material,tag]
        # stiffener_dict = {type : str, dims : [float],mat:str}
        try:
            if len(i['plate'] )== 5:
                tmp_p = cls.plate(i['plate'][0],i['plate'][1],i['plate'][2],i['plate'][3],i['plate'][4])
                if i['plate'][4] != 'Bilge' and 'stiffeners' in i:
                    tmp_d = i['stiffeners']["dimensions"]
                    if len(tmp_d)==2 and i['stiffeners']["type"] == 'fb':
                        dims = {'lw':tmp_d[0],'bw':tmp_d[1]}
                    elif len(tmp_d)==4 and i['stiffeners']["type"] == 'g':
                        dims = {'lw':tmp_d[0],'bw':tmp_d[1],'lf':tmp_d[2],'bf':tmp_d[3]}
                    else: 
                        print("You input a stiffener type that has less dims than needed")
                        continue
                    tmp_s = {'type':i['stiffeners']['type'],'material':i['stiffeners']['material'],'dimensions': dims}
                elif i['plate'][4] == 'Bilge':
                    tmp_s = {}
                else:
                    print(_ERROR_)
                if type(i['id'] ) != int: raise KeyError() # Duplicate check
                if i['id'] in temp_id: 
                    c_error(f'IO.geometry_parser: There was an overlap between the ids of two stiffened plates. \nCONFLICTING ID : '+str(i['id']))
                    raise KeyError()
                tmp = cls.stiff_plate(i['id'],tmp_p,i['spacing'],i['l_pad'],i['r_pad'],tmp_s,i['skip'])
                out.append(tmp)
                temp_id.append(i['id'])
            else:
                raise KeyError()
                # c_error(f"IO.geometry_parser: Loading stiffened plate {i} has resulted in an error. Thus the code will ignore its existence.")
        except KeyError:
            c_error(f"IO.geometry_parser: KeyError: Loading stiffened plate {i} has resulted in an error. The program terminates.")
            quit()

    return out

def blocks_parser(blocks_t:list):
    out = []
    for i in blocks_t:
        try:
            tmp = cls.block(i['type'],i['ids'])
            out.append(tmp)
        except KeyError:
            c_error(f"IO.blocks_parser: KeyError: Loading block {i} has resulted in an error. Thus the code will ignore its existence.")
    return out