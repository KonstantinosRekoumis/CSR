from typing import Iterable

from modules.baseclass.plating.stiff_plate import StiffPlate
from modules.baseclass.plate import _PLACE_
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
            'tb': 'T Bar'
        }
        self.id = stiff_plate.id
        self.name = f'Plate {stiff_plate.id} '
        self.N_st = len(stiff_plate.stiffeners)
        self.tag = _PLACE_[stiff_plate.tag]
        if self.N_st == 0: self.N_st = '-'
        self.plate_material = stiff_plate.plate.material
        self.spacing = round(stiff_plate.spacing * 1e3, 2)
        self.breadth = round(stiff_plate.plate.calc_lna()[1], 3)
        self.breadth_eff = round(stiff_plate.plate.length, 3)
        self.CoA = tuple_round(list(stiff_plate.CoA), 3)
        # Pressure
        self.Pressure = {}
        # Primary stresses 
        self.Ixx_c = round(stiff_plate.n50_Ixx_c * 1e12, 2)
        self.Area = round(stiff_plate.n50_area * 1e6, 2)
        # plate stuff
        self.p_A_n50 = round(stiff_plate.plate.n50_area * 1e6, 4)  # mm^2
        self.p_thick = round(stiff_plate.plate.thickness * 1e3, 4)
        self.p_net_t = round(stiff_plate.plate.net_thickness * 1e3, 4)
        self.p_corr_t = round(stiff_plate.plate.cor_thickness * 1e3, 4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_calc_t = round(stiff_plate.plate.net_thickness_calc * 1e3,
                              4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_empi_t = round(stiff_plate.plate.net_thickness_empi * 1e3,
                              4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_tn50_c = round(stiff_plate.plate.n50_thickness * 1e3, 4) if stiff_plate.tag != 6 else round(
            stiff_plate.plate.thickness * 1e3, 4)
        self.Area_Data = [[self.p_A_n50, tuple_round(stiff_plate.plate.CoA, 2),
                           [round(x * self.p_A_n50, 2) for x in stiff_plate.plate.CoA],
                           round(stiff_plate.plate.n50_Ixx_c * 1e12, 2),
                           round((stiff_plate.plate.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2),
                           round(stiff_plate.plate.n50_Ixx_c * 1e12 + (
                                   stiff_plate.plate.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2)]]
        # stiffener stuff
        if len(stiff_plate.stiffeners) != 0:
            self.stiffener_material = stiff_plate.stiffeners[0].plates[0].material
            self.s_A_n50 = round(stiff_plate.stiffeners[0].n50_area * 1e6, 2)  # mm^2
            self.type = V[stiff_plate.stiffeners[0].type]
            self.Zc = round(stiff_plate.stiffeners[0].calc_Z() * 1e6, 3)
            self.Zrule = round(stiff_plate.stiffeners[0].Z_rule * 1e6, 3)
            self.heights = [round(i.length * 1e3, 4) for i in stiff_plate.stiffeners[0].plates]
            self.s_thick = [round(i.thickness * 1e3, 4) for i in stiff_plate.stiffeners[0].plates]
            self.s_net_t = [round(i.net_thickness * 1e3, 4) for i in stiff_plate.stiffeners[0].plates]
            self.s_corr_t = [round(i.cor_thickness * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_calc_t = [round(i.net_thickness_calc * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_buck_t = [round(i.net_thickness_buck * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_empi_t = [round(i.net_thickness_empi * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_tn50_c = [round(i.n50_thickness * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else [round(i.thickness * 1e3, 2)
                                                                                             for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            for stif in stiff_plate.stiffeners:
                self.Area_Data.append(
                    [self.s_A_n50, tuple_round(stif.CoA, 2), [round(x * self.s_A_n50, 2) for x in stif.CoA],
                     round(stif.n50_Ixx_c * 1e12, 2),
                     round((stif.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.s_A_n50, 2),
                     round(stif.n50_Ixx_c * 1e12 + (stif.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.s_A_n50, 2)])
        self.pressure_append(stiff_plate)

    def update(self, stiff_plate: StiffPlate):
        # Primary stresses 
        self.Ixx_c = round(stiff_plate.n50_Ixx_c * 1e12, 2)
        self.Area = round(stiff_plate.n50_area * 1e6, 2)
        # plate stuff
        self.p_A_n50 = round(stiff_plate.plate.n50_area * 1e6, 4)  # mm^2
        self.p_thick = round(stiff_plate.plate.thickness * 1e3, 4)
        self.p_net_t = round(stiff_plate.plate.net_thickness * 1e3, 4)
        self.p_corr_t = round(stiff_plate.plate.cor_thickness * 1e3, 4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_calc_t = round(stiff_plate.plate.net_thickness_calc * 1e3,
                              4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_empi_t = round(stiff_plate.plate.net_thickness_empi * 1e3,
                              4) if stiff_plate.tag != 6 else 'Not Evaluated'
        self.p_tn50_c = round(stiff_plate.plate.n50_thickness * 1e3, 4) if stiff_plate.tag != 6 else round(
            stiff_plate.plate.thickness * 1e3, 4)
        self.Area_Data = [[self.p_A_n50, tuple_round(stiff_plate.plate.CoA, 2),
                           [round(x * self.p_A_n50, 2) for x in stiff_plate.plate.CoA],
                           round(stiff_plate.plate.n50_Ixx_c * 1e12, 2),
                           round((stiff_plate.plate.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2),
                           round(stiff_plate.plate.n50_Ixx_c * 1e12 + (
                                   stiff_plate.plate.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.p_A_n50, 2)]]
        # stiffener stuff
        if len(stiff_plate.stiffeners) != 0:
            self.s_A_n50 = round(stiff_plate.stiffeners[0].n50_area * 1e6, 2)  # mm^2
            self.Zc = round(stiff_plate.stiffeners[0].calc_Z() * 1e6, 3)
            self.Zrule = round(stiff_plate.stiffeners[0].Z_rule * 1e6, 3) if stiff_plate.tag != 6 else 'Not Evaluated'
            self.s_thick = [round(i.thickness * 1e3, 4) for i in stiff_plate.stiffeners[0].plates]
            self.s_net_t = [round(i.net_thickness * 1e3, 4) for i in stiff_plate.stiffeners[0].plates]
            self.s_corr_t = [round(i.cor_thickness * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_calc_t = [round(i.net_thickness_calc * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_buck_t = [round(i.net_thickness_buck * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_empi_t = [round(i.net_thickness_empi * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else ['Not Evaluated' for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            self.s_tn50_c = [round(i.n50_thickness * 1e3, 4) for i in
                             stiff_plate.stiffeners[0].plates] if stiff_plate.tag != 6 else [round(i.thickness * 1e3, 4)
                                                                                             for i in
                                                                                             stiff_plate.stiffeners[
                                                                                                 0].plates]
            for stif in stiff_plate.stiffeners:
                self.Area_Data.append(
                    [self.s_A_n50, tuple_round(stif.CoA, 2), [round(x * self.s_A_n50, 2) for x in stif.CoA],
                     round(stif.n50_Ixx_c * 1e12, 2),
                     round((stif.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.s_A_n50, 2),
                     round(stif.n50_Ixx_c * 1e12 + (stif.CoA[1] - stiff_plate.CoA[1]) ** 2 * 1e6 * self.s_A_n50, 2)])
        self.pressure_append(stiff_plate)

    def pressure_append(self, stiff_plate: StiffPlate):
        """
        Holds the maximum Pressure value for each EDW across all Loading Conditions
        """
        key_f = lambda x: abs(x[-1])
        if len(self.Pressure) == 0:
            for i in stiff_plate.Pressure:
                tmp = stiff_plate.Pressure[i]
                val = max(tmp, key=key_f)
                self.Pressure[i] = val[-1]
        else:
            for i in stiff_plate.Pressure:
                tmp = stiff_plate.Pressure[i]
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
