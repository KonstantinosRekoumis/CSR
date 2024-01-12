import os
import pytest as pt
from cli import main

PROJECT_ROOT = os.path.split(os.environ['VIRTUAL_ENV'])[0]
MOCK_SHIP_JSON_PATH = os.path.join(PROJECT_ROOT, "out/final.json")


def test_dry_cli_run_doesnt_explode():
    main(MOCK_SHIP_JSON_PATH, False, False, False)

def test_dry_cli_run_export_TeX_Code_doesnt_explode(): 
    main(MOCK_SHIP_JSON_PATH, False, False, True)

def test_dry_cli_ship_pressure_plots_run_doesnt_explode():
    main(MOCK_SHIP_JSON_PATH, True, True, False)
