from typing import Iterable

from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.baseclass.plating.plate import _PLACE_
from modules.utils.decorators import auto_str


def tuple_round(tp: Iterable, dig: int):
    out = []
    for i in tp:
        out.append(round(i, dig))
    return tuple(out)


@auto_str
class DataCell:
    """Wrapper for data export out of a StiffPlate
    """

    def __init__(self, stiff_plate: StiffPlate):
        V = {
            'fb': 'Flat Bar',
            'g': 'Angled Bar',
            'tb': 'T Bar',
            "bb": "Bulbous Bar"
        }
        # Hold the reference to the stiff_plate's components to make life easier
        self.stiff_plate = stiff_plate
        self.base_plate = self.stiff_plate.plate
        self.stiff_groups = self.stiff_plate.stiffener_groups

        self.id = stiff_plate.id
        self.name = f'Plate {stiff_plate.id} '
        self.tag = _PLACE_[stiff_plate.tag]

        self.N_st = [len(i.stiffeners) for i in self.stiff_groups]
        if self.N_st == 0: self.N_st = '-'
        self.plate_material = self.base_plate.material
        self.spacing = round(self.stiff_plate.spacing * 1e3, 2)
        self.breadth = round(self.base_plate.calc_lna()[1], 3)
        self.breadth_eff = round(self.base_plate.length, 3)
        self.CoA = tuple_round(list(stiff_plate.CoA), 3)
        # Pressure
        self.Pressure = {}
        # stiffener stuff
        if len(self.stiff_groups) != 0:
            self.stiffener_material = [i.stiffeners[0].material for i in self.stiff_groups]
            self.type = [V[i.stiffeners[0].type] for i in self.stiff_groups]
            self.heights = [[round(i.length * 1e3, 4) for i in j.stiffeners[0].plates] for j in self.stiff_groups]
        
        self.update()

    def update(self):
        # Primary stresses 
        self.Ixx_c = round(self.stiff_plate.n50_Ixx_c * 1e12, 2)
        self.Area = round(self.stiff_plate.n50_area * 1e6, 2)
        # plate stuff
        self.p_A_n50 = round(self.base_plate.n50_area * 1e6, 4)  # mm^2
        self.p_thick = round(self.base_plate.thickness * 1e3, 4)
        self.p_net_t = round(self.base_plate.net_thickness * 1e3, 4)

        if self.stiff_plate.tag != 6:
            _oper = round
        else: 
            _oper = lambda *args: 'Not Evaluated'

        self.p_corr_t = _oper(self.base_plate.cor_thickness * 1e3, 4)
        self.p_calc_t = _oper(self.base_plate.net_thickness_calc * 1e3, 4)
        self.p_empi_t = _oper(self.base_plate.net_thickness_empi * 1e3, 4)
        self.p_tn50_c = round(self.base_plate.n50_thickness * 1e3, 4) if self.stiff_plate.tag != 6 else round(
            self.base_plate.thickness * 1e3, 4)
        self.Area_Data = [[self.p_A_n50, tuple_round(self.base_plate.CoA, 2),
                           [round(x * self.p_A_n50, 2) for x in self.base_plate.CoA],
                           round(self.base_plate.n50_Ixx_c * 1e12, 2),
                           round((self.base_plate.CoA[1] - self.stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2),
                           round(self.base_plate.n50_Ixx_c * 1e12 + (
                                   self.base_plate.CoA[1] - self.stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2)]]
        # stiffener stuff
        if len(self.stiff_groups) != 0:
            self.s_A_n50 = []
            self.Zc = []
            self.Zrule =[]
            self.s_thick = []
            self.s_net_t = []
            self.s_corr_t = []
            self.s_calc_t = []
            self.s_buck_t = []
            self.s_empi_t = []
            self.s_tn50_c = []
            for st_gr in self.stiff_groups:
                f_st = st_gr.stiffeners[0] 
                _s_A_n50 = round(f_st.n50_area * 1e6, 2)
                self.s_A_n50.append(_s_A_n50) # mm^2
                self.Zc.append(round(f_st.calc_Z() * 1e6, 3))
                self.Zrule.append(_oper(f_st.Z_rule * 1e6, 3))

                self.s_thick.append([round(i.thickness * 1e3, 4) for i in f_st.plates])
                self.s_net_t.append([round(i.net_thickness * 1e3, 4) for i in f_st.plates])
                self.s_corr_t.append([_oper(i.cor_thickness * 1e3, 4) for i in f_st.plates])
                self.s_calc_t.append([_oper(i.net_thickness_calc * 1e3, 4) for i in f_st.plates])
                self.s_buck_t.append([_oper(i.net_thickness_buck * 1e3, 4) for i in f_st.plates])
                self.s_empi_t.append([_oper(i.net_thickness_empi * 1e3, 4) for i in f_st.plates])
                self.s_tn50_c.append([round(i.n50_thickness * 1e3, 4) for i in f_st.plates]
                                      if self.stiff_plate.tag != 6 
                                      else [round(i.thickness * 1e3, 4) for i in f_st.plates])
                
                self.Area_Data.append(
                    [[_s_A_n50, tuple_round(stif.CoA, 2), [round(x * _s_A_n50, 2) for x in stif.CoA],
                    round(stif.n50_Ixx_c * 1e12, 2),
                    round((stif.CoA[1] - self.stiff_plate.CoA[1]) ** 2 * 1e6 * _s_A_n50, 2),
                    round(stif.n50_Ixx_c * 1e12 + (stif.CoA[1] - self.stiff_plate.CoA[1]) ** 2 * 1e6 * _s_A_n50, 2)] for stif in st_gr.stiffeners])
    
        self.pressure_append()

    def pressure_append(self):
        """
        Holds the maximum Pressure value for each EDW across all Loading Conditions
        """
        key_f = lambda x: abs(x[-1])
        if len(self.Pressure) == 0:
            for i in self.stiff_plate.Pressure:
                tmp = self.stiff_plate.Pressure[i]
                val = max(tmp, key=key_f)
                self.Pressure[i] = val[-1]
        else:
            for i in self.stiff_plate.Pressure:
                tmp = self.stiff_plate.Pressure[i]
                val = max(tmp, key=key_f)
                if i in self.Pressure:
                    if abs(self.Pressure[i]) < abs(val[-1]):
                        self.Pressure[i] = val[-1]
                else:
                    self.Pressure[i] = val[-1]

    def get_data(self, mode='Plate', getHeader=True):
        """
        function to return the datacell components as tabular data for the UI
        """
        if mode.lower() == 'plate':
            header = ['Name ', ' Material ', ' Breadth [m] ', ' Stiffener Spacing [mm] '
                , ' CoA [m]', ' Yield Net Thickness [mm] ',
                      ' Minimum Empirical Net Thickness [mm] ', ' Corrosion Thickness [mm]',
                      ' Design Net Thickness [mm]', ' Design Net Thickness + 50% Corrosion [mm] '
                , ' As Built Thickness [mm]']
            data = [self.name, self.plate_material, self.breadth_eff, self.spacing,
                    self.CoA, self.p_calc_t, self.p_empi_t, self.p_corr_t, self.p_net_t,
                    self.p_tn50_c, self.p_thick]
        if getHeader:
            return data, header
        else:
            return data
