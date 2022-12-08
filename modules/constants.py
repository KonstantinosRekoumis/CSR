'''
----------------------------------------------------\n
                    Constants.py\n
An auxiliary file holding various GLOBAL CONSTANTS\n
that would be troublesome and tedious to manually \n
include in each source code file.\n
!!!!!---ONLY TO DECLARE GLOBAL PUBLIC VARIABLES---!!! \n
!! DONT USE AS A CROUCH TO CREATE CASE SPECIFIC CODE !!\n
----------------------------------------------------
'''
#____ CONSTANTS ________
from math import sqrt


RHO_S = 1.025 # tn/m^3 sea water @ 17 Celsius
RHO_F = 0.997 # tn/m^3 fresh water @ 17 Celsius
G = 9.8063 # gravitational acceleration

HEAVY_HOMO = 0.8

LOADS = {
    #Block TAG : {Content Properties}
    'WB' : {'rho':RHO_S,'hair':0.0},
    'DC' : {'rho':HEAVY_HOMO,'fdc':1.0,'psi':30},
    'LC' : {'rho':0.8,'Ppv': 25,'fcd':1.0},
    'OIL': {'rho':0.8,'hair':0.0},
    'FW' : {'rho':RHO_F,'hair':0.0},
    'VOID':{'rho':0.0,'hair':0.0}}

STATIC = {
    'Liquids':['S-NOS','S-HSWO'],
    'Dry':'STATIC',
    'Sea':'STATIC'
}

MATERIALS = {
    # 'type' :('Reh','Rm range'   ,'Teh')
    "A" : (235,(400,520)   ,235/sqrt(3)),
    "AH32" : (315,(440,570),315/sqrt(3)),
    'AH36' : (355,(490,630),355/sqrt(3)),
    'AH40' : (390,(510,660),390/sqrt(3)),
    "D" : (235,(400,520)   ,235/sqrt(3)),
    "DH32" : (315,(440,570),315/sqrt(3)),
    'DH36' : (355,(490,630),355/sqrt(3)),
    'DH40' : (390,(510,660),390/sqrt(3)),
    "E" : (235,(400,520)   ,235/sqrt(3)),
    "EH32" : (315,(440,570),315/sqrt(3)),
    'EH36' : (355,(490,630),355/sqrt(3)),
    'EH40' : (390,(510,660),390/sqrt(3))
}

TEX_PREAMBLE = (
'\\documentclass[12pt,a4paper]{report}\n'
'\\usepackage[a4paper,headheight =15pt]{geometry}\n'
'\\usepackage{array}\n'
'\\usepackage{multirow}\n'
'\\usepackage{longtable}\n'
'\\usepackage{pdflscape}\n'
'\\usepackage{amsmath}\n'
'\\usepackage{comment}\n'
'\\usepackage{caption}\n'
'\\usepackage{graphicx}\n'
'\\usepackage{fancyhdr}\n'
'\\usepackage{typearea}\n'
'\\usepackage[absolute]{textpos}\n'
'\\fancypagestyle{normal}{\\fancyhf{}\\rhead{\\thepage}\\lhead{\\leftmark}\\setlength{\\headheight}{15pt}\n'
'\\renewcommand{\\headrulewidth}{1pt} \n'
'\\renewcommand{\\footrulewidth}{0pt}}\n'
'\\fancypagestyle{lscape}{% \n'
'\\fancyhf{} % clear all header and footer fields \n'
'\\fancyhead[L]{%\n'
'\\begin{textblock}{0}(1,12){\\rotatebox{90}{\\underline{\\leftmark}}}\\end{textblock}\n'
'\\begin{textblock}{2}(1,1){\\rotatebox{90}{\\underline{\\thepage}}}\\end{textblock}}\n'
'\\setlength{\\headheight}{15pt}\n'
'\\setlength{\\footheight}{0pt}\n'
'\\renewcommand{\\headrulewidth}{0pt} \n'
'\\renewcommand{\\footrulewidth}{0pt}}\n'
'\\graphicspath{{./}}\n'
)