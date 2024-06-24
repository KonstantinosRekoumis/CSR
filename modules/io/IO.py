import json

from modules.baseclass.block import Block, LOAD_SPACE_TYPE
from modules.baseclass.plating.stiff_plate import StiffPlate, StiffGroup
from modules.baseclass.plating.stiffener import Stiffener
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
    save = '{"id":' + str(stiff_plate.id) + ',"plate":' + plate_save(stiff_plate.plate) + ","
    if len(stiff_plate.stiffeners) != 0:
        save += '"stiffeners":' + stiff_save(stiff_plate.stiffeners[0]) + ","
    else:
        save += '"stiffeners": {},'

    save += '"spacing":' + json.dumps(stiff_plate.spacing * 1e3) + ","
    save += '"psm_spacing":' + json.dumps(stiff_plate.psm_spacing) + ","
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
    for st_pl_dict in geo_t:
        tmp_p = load_plate(st_pl_dict["plate"])
        tmp_s = [load_stiff_group(data) for data in st_pl_dict["stiffeners"]]
        if st_pl_dict['id'] is int:
            Logger.error(f'Id is not an integer')
        if st_pl_dict['id'] in temp_id:
            Logger.error(
                f'There was an overlap between the '
                f'ids of two stiffened plates. \nCONFLICTING ID : ' + str(st_pl_dict['id']))
        if 'null' in st_pl_dict:
            null = st_pl_dict['null']
        else:
            null = False
        tmp = StiffPlate(st_pl_dict['id'], tmp_p, tmp_s, st_pl_dict['psm_spacing'], null=null)
        out.append(tmp)
        temp_id.append(st_pl_dict['id'])

    return out

def load_stiff_group(data_dict: list[dict[str, any]], plate: Plate) -> StiffGroup:
    keys = {0: 'lw' , 1: 'bw' , 2: 'lf' , 3: 'bf' }
    stiff_types = {"fb": 2, "g": 4, "t": 4, "bb": 3}
    if plate.tag != 'Bilge' and len(data_dict) != 0:
        # extra dimensions than the first N required are omitted
        stiff_dict = data_dict["stiffener_type"]
        try:
            min_dims = 0
            if stiff_dict["type"] in stiff_types:
                min_dims = stiff_types[stiff_dict["type"]]
            else:
                Logger.error(f"Invalid type of stiffener was used! {stiff_dict["type"]} is not a valid abbreviation")
            assert (len(stiff_dict["dimensions"]) >= min_dims), "Your stiffener has not enough dimensions!"
            # check if KeyError will rise
            for index in range(len(stiff_dict["dimensions"])):
                stiff_dict["dimensions"][index]
        except KeyError:
            Logger.error(f"The dimensions dict is not properly formatted! {stiff_dict["dimensions"]}")
        except AssertionError as ae:
            Logger.error("", rethrow=ae)

        return StiffGroup(**{"plate": plate, **data_dict})
    elif data_dict['plate']["tag"] == 'Bilge' or len(data_dict) == 0:
        return None
    else:
        Logger.error('Error loading stiffeners.')

def load_plate(kwargs: dict[str, any]) -> Plate:
    if len(kwargs) < 5:
        Logger.error(f'Plate has no correct format.')

    if kwargs["start"] == kwargs["end"]:
        Logger.error(f'Plate :{kwargs} You cannot enter a plate with no length!')

    if kwargs["material"] not in MATERIALS:
        Logger.error(f'Plate :{kwargs["plate"]} Your plate has a no documented material !')

    t = kwargs["thickness"] if kwargs["thickness"] != 0 else 0.1
    return Plate(**kwargs)



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
