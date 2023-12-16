from math import sqrt

RHO_S = 1.025  # tn/m^3 seawater @ 17 Celsius
RHO_F = 0.997  # tn/m^3 fresh water @ 17 Celsius
G = 9.8063  # gravitational acceleration
HEAVY_HOMO = 0.8
LOADS = {
    # Block TAG : {Content Properties}
    'WB': {'rho': RHO_S, 'hair': 0.0},
    'DC': {'rho': HEAVY_HOMO, 'fdc': 1.0, 'psi': 30},
    'LC': {'rho': 0.8, 'Ppv': 25, 'fcd': 1.0},
    'OIL': {'rho': 0.8, 'hair': 0.0},
    'FW': {'rho': RHO_F, 'hair': 0.0},
    'VOID': {'rho': 0.0, 'hair': 0.0}}
STATIC = {
    'Liquids': ['S-NOS', 'S-HSWO'],
    'Dry': 'STATIC',
    'Sea': 'STATIC'
}
MATERIALS = {
    # 'type' :('Reh','Rm range'   ,'Teh')
    "A": (235, (400, 520), 235 / sqrt(3)),
    "AH32": (315, (440, 570), 315 / sqrt(3)),
    'AH36': (355, (490, 630), 355 / sqrt(3)),
    'AH40': (390, (510, 660), 390 / sqrt(3)),
    "D": (235, (400, 520), 235 / sqrt(3)),
    "DH32": (315, (440, 570), 315 / sqrt(3)),
    'DH36': (355, (490, 630), 355 / sqrt(3)),
    'DH40': (390, (510, 660), 390 / sqrt(3)),
    "E": (235, (400, 520), 235 / sqrt(3)),
    "EH32": (315, (440, 570), 315 / sqrt(3)),
    'EH36': (355, (490, 630), 355 / sqrt(3)),
    'EH40': (390, (510, 660), 390 / sqrt(3))
}
