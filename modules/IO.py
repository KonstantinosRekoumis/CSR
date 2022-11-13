from modules.constants import MATERIALS
from modules.utilities import _ERROR_,_RESET_,_WARNING_,c_error,c_warn
import modules.classes as cls
import modules.render as rnr
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
    save += '\"r_pad\":'+json.dumps(stiff_plate.r_pad*1e3)
    if stiff_plate.null: save += ","+'\"null\":'+json.dumps(stiff_plate.null)
    return save+"}"

def blocks_save(block:cls.block):
    save =""
    save += "{\"name\":\""+block.name+"\",\"symmetrical\":"+json.dumps(block.symmetrical)+",\"type\":\""+block.space_type+"\",\"ids\":"+json.dumps(block.list_plates_id)+"}"
    return save

def section_save(ship:cls.ship):
    save = '\"geometry\":[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i)+',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'
    #Added Blocks feature
    save += ',\n\"blocks\":[\n'
    for i in ship.blocks:
        if (i.space_type != "SEA")and(i.space_type != "ATM"):
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
    save += "\"PSM_spacing\":"+str(ship.PSM_spacing)+',\n'

    save += section_save(ship) +"\n}"

    with open(filename,'w') as file:
        file.write(save)


def load_ship(filename):
    with open(filename,'r') as file:
        data = json.loads(file.read())
    tags = ['LBP','Lsc','B','T','Tmin','Tsc','D','Cb','Cp','Cm','DWT','PSM_spacing']
    particulars = []
    for i in tags:
        try:
            particulars.append(data[i])
        except KeyError:
            c_error(f"The input file is not appropriately formatted, and it is missing crucial data.\n Value: \'{i}\' is missing.")
            quit()
    try:
        stiff_plates = geometry_parser(data['geometry'])
        if len(stiff_plates) == 0:
            c_error("Check your input file")
            quit()
    except KeyError:
        c_error("The input file is not appropriately formatted, and it is missing crucial data.\n Value: 'geometry' is missing.")
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
            if len(i['plate'] ) >= 5:
                if (i['plate'][0] == i['plate'][1]): 
                    plate = i['plate']
                    c_error(f'(IO.py) geometry_parser: Plate :{plate} You cannot enter a plate with no length!')
                    quit()
                elif i['plate'][3] not in MATERIALS:
                    plate = i['plate']
                    c_error(f'(IO.py) geometry_parser: Plate :{plate} Your plate has a no documented material !')
                    quit()
                t = i['plate'][2] if i['plate'][2] != 0 else 0.1
                tmp_p = cls.plate(i['plate'][0],i['plate'][1],t,i['plate'][3],i['plate'][4])
                if i['plate'][4] != 'Bilge' and 'stiffeners' in i and  len(i['stiffeners']) != 0:
                    tmp_d = i['stiffeners']["dimensions"]
                    if len(tmp_d)==2 and i['stiffeners']["type"] == 'fb':
                        dims = {'lw':tmp_d[0],'bw':tmp_d[1]}
                    elif len(tmp_d)==4 and i['stiffeners']["type"] in ('g','tb'):
                        dims = {'lw':tmp_d[0],'bw':tmp_d[1],'lf':tmp_d[2],'bf':tmp_d[3]}
                    else: 
                        c_error("(IO.py) You input a stiffener type that has less dims than needed",i['stiffeners'])
                        raise KeyError()
                    tmp_s = {'type':i['stiffeners']['type'],'material':i['stiffeners']['material'],'dimensions': dims}
                elif i['plate'][4] == 'Bilge' or len(i['stiffeners']) == 0:
                    tmp_s = {}
                else:
                    c_error('(IO.py) geometry_parser: Error loading stiffeners.')
                    raise KeyError()
                if type(i['id'] ) != int: 
                    c_error(f'(IO.py) geometry_parser: Id is not an integer')
                    raise KeyError() # Duplicate check
                if i['id'] in temp_id: 
                    c_error(f'(IO.py) geometry_parser: There was an overlap between the ids of two stiffened plates. \nCONFLICTING ID : '+str(i['id']))
                    raise KeyError()
                if 'null' in i:
                    null = i['null']
                else:
                    null = False
                tmp = cls.stiff_plate(i['id'],tmp_p,i['spacing'],i['l_pad'],i['r_pad'],tmp_s,i['skip'],null=null)
                out.append(tmp)
                temp_id.append(i['id'])
            else:
                c_error(f'(IO.py) geometry_parser: Plate has no correct format.')
                raise KeyError()
                # c_error(f"IO.geometry_parser: Loading stiffened plate {i} has resulted in an error. Thus the code will ignore its existence.")
        except KeyError:
            c_error(f"(IO.py) geometry_parser: KeyError: Loading stiffened plate {i} has resulted in an error. The program terminates.")
            quit()

    return out

def blocks_parser(blocks_t:list):
    out = []
    for i in blocks_t:
        try:
            tmp = cls.block(i['name'],i['symmetrical'],i['type'],i['ids'])
            out.append(tmp)
        except KeyError:
            c_error(f"(IO.py) blocks_parser: KeyError: Loading block {i} has resulted in an error. Thus the code will ignore its existence.")
    return out

def LaTeX_output(ship:cls.ship,path='./',_standalone = True):
    out = ship.LaTeX_output(standalone=_standalone,figs=('id_plt.pdf','tag_plt.pdf'))
    with open(path+'tabs.tex','w') as file:
            file.write(out)
    rnr.contour_plot(ship,key="id",path=path+'id_plt.pdf')
    rnr.contour_plot(ship,key="tag",path=path+'tag_plt.pdf')