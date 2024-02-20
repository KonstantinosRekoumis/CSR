import json

from modules.baseclass.block import Block, LOAD_SPACE_TYPE
from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.baseclass.stiffener import Stiffener
from modules.baseclass.plating.plate import Plate
from modules.baseclass.ship import Ship
from modules.utils.constants import MATERIALS
from modules.utils.logger import Logger
from modules.utils.operations import set_diff


def plate_save(plate: Plate):
    # Save data to JSON format
    return json.dumps(plate.save_data())


def stiff_save(stiff: Stiffener):
    # Save data to JSON format
    dim = []
    for i in stiff.plates:
        dim.append(i.length * 1e3)
        dim.append(i.thickness * 1e3)

    return json.dumps({'type': stiff.type, 'dimensions': dim, 'material': stiff.plates[0].material})


def stiff_pl_save(stiff_plate: StiffPlate):
    save = ""
    save += '{"id":' + str(stiff_plate.id) + ',"plate":' + plate_save(stiff_plate.plate) + ","
    if len(stiff_plate.stiffeners) != 0:
        save += '"stiffeners":' + stiff_save(stiff_plate.stiffeners[0]) + ","
    else:
        save += '"stiffeners": {},'

    save += '"spacing":' + json.dumps(stiff_plate.spacing * 1e3) + ","
    save += '"PSM_spacing":' + json.dumps(stiff_plate.PSM_spacing) + ","
    save += '"skip":' + json.dumps(stiff_plate.skip) + ","
    save += '"s_pad":' + json.dumps(stiff_plate.s_pad * 1e3) + ","
    save += '"e_pad":' + json.dumps(stiff_plate.e_pad * 1e3)
    if stiff_plate.null: save += "," + '"null":' + json.dumps(stiff_plate.null)
    return save + "}"


def blocks_save(block: Block):
    save = {
        "name" : block.name,
        "symmetrical" : block.symmetrical,
        "type" : str(block.space_type),
        "ids" : block.list_plates_id
    }
    # save = ""
    # save += '{"name":"' + block.name + '","symmetrical":' + json.dumps(
    #     block.symmetrical) + ',"type":"' + str(block.space_type) + '","ids":' + json.dumps(block.list_plates_id) + "}"
    return json.dumps(save)


def section_save(ship: Ship):
    save = '"geometry":[\n'
    for i in ship.stiff_plates[:-1]:
        save += stiff_pl_save(i) + ',\n'
    save += stiff_pl_save(ship.stiff_plates[-1]) + '\n]'
    # Added Blocks feature
    save += ',\n"blocks":[\n'
    for i in ship.blocks:
        if (i.space_type != "SEA") and (i.space_type != "ATM"):
            save += blocks_save(i) + ',\n'
    save = save[:-2] + '\n]'

    return save


def ship_save(ship: Ship, filename: str):
    save = '{"LBP":' + str(ship.LBP) + ',\n'
    save += '"Lsc":' + str(ship.Lsc) + ',\n'
    save += '"B":' + str(ship.B) + ',\n'
    save += '"T":' + str(ship.T) + ',\n'
    save += '"Tmin":' + str(ship.Tmin) + ',\n'
    save += '"Tsc":' + str(ship.Tsc) + ',\n'
    save += '"D":' + str(ship.D) + ',\n'
    save += '"Cb":' + str(ship.Cb) + ',\n'
    save += '"Cp":' + str(ship.Cp) + ',\n'
    save += '"Cm":' + str(ship.Cm) + ',\n'
    save += '"DWT":' + str(ship.DWT) + ',\n'
    save += section_save(ship) + "\n}"

    with open(filename, 'w') as file:
        file.write(save)


def load_ship(filename):
    with open(filename, 'r') as file:
        data = json.loads(file.read())
    tags = ['LBP', 'Lsc', 'B', 'T', 'Tmin', 'Tsc', 'D', 'Cb', 'Cp', 'Cm', 'DWT']

    sd = set_diff(tags + ["geometry", "blocks"], data.keys())
    if sd:
        Logger.error(
            f"The input file is not appropriately formatted, and it is missing crucial data. "
            f"Keys {sd} are missing."
        )

    particulars = []
    for tag in tags:
        particulars.append(data[tag])

    stiff_plates = geometry_parser(data['geometry'])

    blocks = blocks_parser(data['blocks'])
    if not blocks:
        Logger.error("Check your input file")

    return Ship(*particulars, stiff_plates=stiff_plates, blocks=blocks)


def geometry_parser(geo_t: list):
    out = []
    temp_id = []
    for i in geo_t:
        if len(i['plate']) < 5:
            Logger.error(f'Plate has no correct format.')

        if i['plate'][0] == i['plate'][1]:
            Logger.error(f'Plate :{i["plate"]} You cannot enter a plate with no length!')

        if i['plate'][3] not in MATERIALS:
            Logger.error(f'Plate :{i["plate"]} Your plate has a no documented material !')

        t = i['plate'][2] if i['plate'][2] != 0 else 0.1
        tmp_p = Plate(i['plate'][0], i['plate'][1], t, i['plate'][3], i['plate'][4])
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
                    "You input a stiffener type that has less dims than needed",
                    i['stiffeners']
                )
            tmp_s = {
                'type': i['stiffeners']['type'], 'material': i['stiffeners']['material'],
                'dimensions': dims
            }
        elif i['plate'][4] == 'Bilge' or len(i['stiffeners']) == 0:
            tmp_s = {}
        else:
            Logger.error('Error loading stiffeners.')
        if i['id'] is int:
            Logger.error(f'Id is not an integer')
        if i['id'] in temp_id:
            Logger.error(
                f'There was an overlap between the '
                f'ids of two stiffened plates. \nCONFLICTING ID : ' + str(i['id']))
        if 'null' in i:
            null = i['null']
        else:
            null = False
        tmp = StiffPlate(i['id'], tmp_p, i['spacing'], i['s_pad'], i['e_pad'], tmp_s, i['skip'],
                         i['PSM_spacing'], null=null)
        out.append(tmp)
        temp_id.append(i['id'])

    return out


def blocks_parser(blocks_t: list):
    required_keys = ["name", "symmetrical", "type", "ids"]
    out = []
    for block in blocks_t:
        if set_diff(required_keys, block):
            Logger.error("Loading block {block} has resulted in an error.")
        space_type = LOAD_SPACE_TYPE[block['type']]
        tmp = Block(block['name'], block['symmetrical'], space_type, block['ids'])
        out.append(tmp)

    return out
