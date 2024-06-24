import json
from logging import Logger
from modules.baseclass import block
from modules.baseclass.plating.plate import Plate
from modules.io import IO
import os

from modules.utils.operations import set_diff

PROJECT_ROOT = os.path.split(os.environ['VIRTUAL_ENV'])[0]
MOCK_SHIP_JSON_PATH = os.path.join(PROJECT_ROOT, "out/final.json")

def test_plate_IO():
    """
    Test to check whether the save/load system is broken or not
    """
    modes = ["LINEAR", "QUART_C"]
    mock_plate = {'start': [0, 1], 'end': [1, 0], 'thickness': 1.0, 'material': 'AH32', 'tag': 'Shell', 'prefix': 'LINEAR'}
    for m in modes:
        mock_plate["prefix"] = m
        IO.load_plate(Plate(**mock_plate).save_data())

def test_Block_IO():
    with open(MOCK_SHIP_JSON_PATH, 'r') as file:
        data = json.loads(file.read())
    blocks = IO.blocks_parser(data['blocks'])

def test_ship_IO():
    papor = IO.load_ship(MOCK_SHIP_JSON_PATH)
    
