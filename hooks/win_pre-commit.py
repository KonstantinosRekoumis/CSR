import os 
from subprocess import run, PIPE
import pytest as pt
from datetime import datetime as dt

'''
Abbibas version of the pre-commit shell script for the avg Windows user. (no i
dont intend to learn how to write a .bat file)
'''


root_dir = run(["git", "rev-parse", "--show-toplevel"], stdout=PIPE)
smoke_test_dir = os.path.join(root_dir, "tests", "smoke")
logs_dir = os.path.join(root_dir, "logs")
output_xml = os.path.join(logs_dir, f"tests_{dt.now().strftime("%H_%M_%S")}.xml")
output_html = os.path.join(logs_dir, f"tests_{dt.now().strftime("%H_%M_%S")}.html")
output_basic_html = os.path.join(logs_dir, f"tests_basic_{dt.now().strftime("%H_%M_%S")}.html")

