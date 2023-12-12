import json

from modules.baseclass import plate, block, ship
import modules.render as rnr
from modules.constants import MATERIALS
from modules.utilities import Logger


def plate_save(plate: plate.Plate):
    # Save data to JSON format
    return json.dumps(plate.save_data())


def stiff_save(stiff: plate.Stiffener):
    # Save data to JSON format
    dim = []
    for i in stiff.plates:
        dim.append(i.length * 1e3)
        dim.append(i.thickness * 1e3)

    return json.dumps({'type': stiff.type, 'dimensions': dim, 'material': stiff.plates[0].material})


def stiff_pl_save(stiff_plate: plate.StiffPlate):
    save = ""
    save += '{\"id\":' + str(stiff_plate.id) + ',\"plate\":' + plate_save(stiff_plate.plate) + ","
    if len(stiff_plate.stiffeners) != 0:
        save += '\"stiffeners\":' + stiff_save(stiff_plate.stiffeners[0]) + ","
    else:
        save += '\"stiffeners\": {},'

    save += '\"spacing\":' + json.dumps(stiff_plate.spacing * 1e3) + ","
    save += '\"PSM_spacing\":' + json.dumps(stiff_plate.PSM_spacing) + ","
    save += '\"skip\":' + json.dumps(stiff_plate.skip) + ","
    save += '\"s_pad\":' + json.dumps(stiff_plate.s_pad * 1e3) + ","
    save += '\"e_pad\":' + json.dumps(stiff_plate.e_pad * 1e3)
    if stiff_plate.null: save += "," + '\"null\":' + json.dumps(stiff_plate.null)
    return save + "}"


def blocks_save(block: block.Block):
    save = ""
    save += "{\"name\":\"" + block.name + "\",\"symmetrical\":" + json.dumps(
        block.symmetrical) + ",\"type\":\"" + block.space_type + "\",\"ids\":" + json.dumps(block.list_plates_id) + "}"
    return save


def section_save(ship: ship.Ship):
    save = '\"geometry\":[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i) + ',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'
    # Added Blocks feature
    save += ',\n\"blocks\":[\n'
    for i in ship.blocks:
        if (i.space_type != "SEA") and (i.space_type != "ATM"):
            save += blocks_save(i) + ',\n'
    save = save[:-2] + '\n]'

    return save


def ship_save(ship: ship.Ship, filename: str):
    save = "{\"LBP\":" + str(ship.LBP) + ',\n'
    save += "\"Lsc\":" + str(ship.Lsc) + ',\n'
    save += "\"B\":" + str(ship.B) + ',\n'
    save += "\"T\":" + str(ship.T) + ',\n'
    save += "\"Tmin\":" + str(ship.Tmin) + ',\n'
    save += "\"Tsc\":" + str(ship.Tsc) + ',\n'
    save += "\"D\":" + str(ship.D) + ',\n'
    save += "\"Cb\":" + str(ship.Cb) + ',\n'
    save += "\"Cp\":" + str(ship.Cp) + ',\n'
    save += "\"Cm\":" + str(ship.Cm) + ',\n'
    save += "\"DWT\":" + str(ship.DWT) + ',\n'
    save += section_save(ship) + "\n}"

    with open(filename, 'w') as file:
        file.write(save)


def load_ship(filename, file=None):
    with open(filename, 'r') as file:
        data = json.loads(file.read())
    tags = ['LBP', 'Lsc', 'B', 'T', 'Tmin', 'Tsc', 'D', 'Cb', 'Cp', 'Cm', 'DWT']  # ,'PSM_spacing']
    particulars = []
    for i in tags:
        try:
            particulars.append(data[i])
        except KeyError:
            Logger.error(
                f"The input file is not appropriately formatted, "
                f"and it is missing crucial data.\n Value: \'{i}\' is missing.")
            quit()
    try:
        stiff_plates = geometry_parser(data['geometry'])
        if len(stiff_plates) == 0:
            Logger.error("Check your input file")
            quit()
    except KeyError:
        Logger.error(
            "The input file is not appropriately formatted, and "
            "it is missing crucial data.\n Value: 'geometry' is missing.")
        quit()
    try:
        blocks = blocks_parser(data['blocks'])
        if len(blocks) == 0:
            print(ERROR, "Check your input file", RESET)
            quit()
    except KeyError:
        print(ERROR,
              "The input file is not appropriately formatted, "
              "and it is missing crucial data.\n Value: 'geometry' is missing.",
              RESET)
        quit()

    return ship.Ship(*particulars, stiff_plates, blocks)


def geometry_parser(geo_t: list):
    out = []
    temp_id = []
    for i in geo_t:
        # i['plate'] = [start,end,thickness,material,tag]
        # stiffener_dict = {type : str, dims : [float],mat:str}
        try:
            if len(i['plate']) >= 5:
                if i['plate'][0] == i['plate'][1]:
                    Logger.error(f'(IO.py) geometry_parser: Plate :{i["plate"]} You cannot enter a plate with no length!')
                    quit()
                elif i['plate'][3] not in MATERIALS:
                    Logger.error(f'(IO.py) geometry_parser: Plate :{i["plate"]} Your plate has a no documented material !')
                    quit()
                t = i['plate'][2] if i['plate'][2] != 0 else 0.1
                tmp_p = plate.Plate(i['plate'][0], i['plate'][1], t, i['plate'][3], i['plate'][4])
                if i['plate'][4] != 'Bilge' and 'stiffeners' in i and len(i['stiffeners']) != 0:
                    tmp_d = i['stiffeners']["dimensions"]
                    # extra dimensions than the first N required are omitted
                    if len(tmp_d) >= 2 and i['stiffeners']["type"] == 'fb':
                        dims = {'lw': tmp_d[0], 'bw': tmp_d[1]}
                    # extra dimensions than the first N required are omitted
                    elif len(tmp_d) >= 4 and i['stiffeners']["type"] in ('g', 'tb'):
                        dims = {'lw': tmp_d[0], 'bw': tmp_d[1], 'lf': tmp_d[2], 'bf': tmp_d[3]}
                    else:
                        Logger.error(
                            "(IO.py) You input a stiffener type that has less dims than needed",
                            i['stiffeners']
                        )
                        raise KeyError()
                    tmp_s = {
                        'type': i['stiffeners']['type'], 'material': i['stiffeners']['material'],
                        'dimensions': dims
                    }
                elif i['plate'][4] == 'Bilge' or len(i['stiffeners']) == 0:
                    tmp_s = {}
                else:
                    Logger.error('(IO.py) geometry_parser: Error loading stiffeners.')
                    raise KeyError()
                if i['id'] is int:
                    Logger.error(f'(IO.py) geometry_parser: Id is not an integer')
                    raise KeyError()  # Duplicate check
                if i['id'] in temp_id:
                    Logger.error(
                        f'(IO.py) geometry_parser: There was an overlap between the '
                        f'ids of two stiffened plates. \nCONFLICTING ID : ' + str(i['id']))
                    raise KeyError()
                if 'null' in i:
                    null = i['null']
                else:
                    null = False
                tmp = plate.StiffPlate(i['id'], tmp_p, i['spacing'], i['s_pad'], i['e_pad'], tmp_s, i['skip'],
                                     i['PSM_spacing'], null=null)
                out.append(tmp)
                temp_id.append(i['id'])
            else:
                Logger.error(f'(IO.py) geometry_parser: Plate has no correct format.')
                raise KeyError()
        except KeyError:
            Logger.error(
                f"(IO.py) geometry_parser: KeyError: Loading stiffened plate {i} "
                f"has resulted in an error. The program terminates."
            )
            quit()

    return out


def blocks_parser(blocks_t: list):
    out = []
    for i in blocks_t:
        try:
            tmp = block.Block(i['name'], i['symmetrical'], i['type'], i['ids'])
            out.append(tmp)
        except KeyError:
            Logger.error(
                f"(IO.py) blocks_parser: KeyError: Loading block {i} "
                f"has resulted in an error. Thus the code will ignore its existence."
            )
    return out
