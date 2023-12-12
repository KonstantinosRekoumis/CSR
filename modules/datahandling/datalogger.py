import numpy as np
from modules.baseclass.ship import Ship
from modules.constants import LOADS, TEX_PREAMBLE
from modules.datahandling.datacell import DataCell
from modules.utilities import Logger


class DataLogger:
    """
    Datalogging class that acts as Grabber of the DataCell contained in each stiff plate.
    Creates tabular data for export. TO BE USED after the calculations are already done.
    IF NOT won't yield useful results.

    TODO : Utilize the Datalogger for the Data Tables in the GUI as a Singleton
    """

    def plate_name(self, cell: DataCell):
        return int(cell.name[6:])

    def __init__(self, ship: Ship):
        self.conds = []  # EDWs that were documented
        self.Cells = []
        self.Press_D = []
        self.Plate_D = []
        self.Stiff_D = []
        self.St_Pl_D = []
        self.PrimS_D = []
        self.ship = ship
        self.LoadData()


    def LoadData(self):
        self.Cells = []  # may be slow for performance but it is meant to be called 1-2 times per main run
        for st_pl in self.ship.stiff_plates:
            if st_pl.null: continue
            self.Cells.append(DataCell(st_pl))
        self.Cells.sort(key=self.plate_name)
    
    def LoadConds(self, _conds: list[str]):
        """Load the physics conditions evaluated

        Args:
            _conds (list[str]): The physics conditions evaluated
            !!! ONLY INPUT THE CONDITIONS THAT HAVE RUN !!!
        """
        self.conds = _conds

    def CreateTabularData(self, dump=False):
        """
        It updates the DataLogger as well
        Press_D : Name & Breadth [m] & CoA [m] (y,z) & HSM-1 & ... & EDW-last & Max Pressure
        Plate_D : Name & Material & Breadth [m] & Stiffener Spacing [mm] & CoA [m]
                    & Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm] & Corrosion Thickness [mm]
                    & Design Net Thickness [mm]& Design Net Thickness + 50% Corrosion [mm] & As Built Thickness [mm]
        Stiff_D : Name & Material & Type & Z actual [cm^3] & Z rule [cm^3] & Web | Flange &
                    Length [mm] & & Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm]
                    Buckling Net Thickness [mm] & Corrosion Thickness [mm] & Design Net Thickness [mm]
                    & Design Net Thickness + 50% Corrosion [mm] & As Built Thickness [mm]
        St_Pl_D : Name & Plate | St 1,2,..,N | St_plate & Area n-50 [mm^2] & CoA [m] (y,z) & Moments of Area [cm^3]
                    & ixx,c [mm^4] & Area*(x_{CoA}*10^3)^2 [mm^4] & ixx,pl [mm^4]
        PrimS_D : Name & & Area n-50 [mm^2] & CoA [m] (y,z) & Moments of Area [cm^3]
                    & Ixx,c [mm^4] & Area*(x_{CoA}*10^3)^2 [mm^4] & ixx,pl [mm^4]
        """

        def max_p(l):
            max_ = -1e8
            for i in l:
                try:
                    if abs(max_) < abs(i): max_ = i
                except TypeError:
                    continue
            if max_ == -1e8: return 'Not Evaluated'
            return max_

        # reset tables
        self.Press_D = []
        self.Plate_D = []
        self.Stiff_D = []
        self.St_Pl_D = []
        self.PrimS_D = []
        # load/update data 
        self.LoadData(self.ship)
        _ship = self.ship # ugly solution to an even uglier problem

        for i, cell in enumerate(self.Cells):
            p = []

            for cond in self.conds:
                if cond in cell.Pressure:
                    p.append(round(cell.Pressure[cond], 2))
                else:
                    p.append('-')

            if len(self.Plate_D) == 0:
                # Plate Group Initial ( Annotation Purpose only !)
                self.Press_D.append(cell.tag)
                self.Plate_D.append(cell.tag)
                self.Stiff_D.append(cell.tag)
                self.St_Pl_D.append(cell.tag)
                self.PrimS_D.append(cell.tag)
            else:
                # Shift to new group ( Annotation Purpose only !)
                if self.Cells[i - 1].tag != cell.tag:
                    self.Press_D.append(cell.tag)
                    self.Plate_D.append(cell.tag)
                    self.Stiff_D.append(cell.tag)
                    self.St_Pl_D.append(cell.tag)
                    self.PrimS_D.append(cell.tag)
            # Pressure Table
            self.Press_D.append([cell.name, cell.breadth, cell.CoA, *p, max_p(p)])
            # Plating Table
            self.Plate_D.append([cell.name, cell.plate_material, cell.breadth_eff, cell.spacing, cell.CoA, max_p(p),
                                 cell.p_calc_t, cell.p_empi_t, cell.p_corr_t, cell.p_net_t, cell.p_tn50_c,
                                 cell.p_thick])
            # Stiffened Plate Table
            self.St_Pl_D.append([cell.name, 'Main Plate', *cell.Area_Data[0]])
            for j in range(1, len(cell.Area_Data)): self.St_Pl_D.append(
                [cell.name, f'Stiffener : {j}', *cell.Area_Data[j]])
            self.St_Pl_D.append(
                [cell.name, 'Total St. Plate Sums:', cell.Area, cell.CoA, [round(x * cell.Area, 2) for x in cell.CoA],
                 '', '', cell.Ixx_c])
            # Stiffeners Table
            if cell.N_st != '-':
                tmp = [cell.name, cell.stiffener_material, cell.type, cell.Zc, cell.Zrule]
                for j in range(len(cell.s_empi_t)):
                    tmp.append([cell.heights[j], cell.s_calc_t[j], cell.s_empi_t[j],
                                cell.s_buck_t[j], cell.s_corr_t[j], cell.s_net_t[j], cell.s_tn50_c[j], cell.s_thick[j]])
                self.Stiff_D.append(tmp)
            self.PrimS_D.append([cell.name, cell.Area, cell.CoA, [round(x * cell.Area, 2) for x in cell.CoA],
                                 cell.Ixx_c, cell.Area * (cell.CoA[1] - _ship.yo) ** 2,
                                 cell.Ixx_c + cell.Area * (cell.CoA[1] - _ship.yo) ** 2])
        self.PrimS_D.append(['Total Sums :', _ship.cross_section_area * 1e6, (_ship.xo, _ship.yo),
                             (round(_ship.xo * _ship.cross_section_area * 1e6, 2),
                              round(_ship.yo * _ship.cross_section_area * 1e6, 2)), ' ', ' ',
                             _ship.n50_Ixx * 1e12])
        if dump:
            return self.Press_D, self.Plate_D, self.Stiff_D, self.St_Pl_D, self.PrimS_D

    def latex_output(self, Debug=False):
        endl = '\\tabularnewline\\hline\n'

        def bold(a):
            return '\\textbf{' + a + '}'

        def f(a):
            if type(a) in (int, float, np.float64, np.float32):
                return f'{a:0.4g}'
            elif type(a) in (list, tuple) and len(a) <= 2:
                out = '('
                for i in a: out += f(i) + ', '
                return out[:-2] + ')'
            elif type(a) == str:
                return a
            else:
                Logger.warning(
                    f'(classes.py) DataLogger/LaTeX_output/f: Variable {a} of {type(a)} is not supported. Thus f() will return value None.')

        def tabular(data, clmns, header):
            out = header
            for line in data:
                _bold = False
                if type(line) == list:
                    if type(line[-1]) == list and len(line[-1]) > 2:  # Stiffeners Data
                        s = -1  # slice
                        if type(line[-2]) == list and len(line[-2]) > 2:
                            s = -2
                        c = 0
                        if s == -2:
                            for elem in line[:s]:
                                elem = f(elem)
                                c += 1
                                out += '\\multirow{' + str(abs(s)) + '}{*}{' + str(elem) + ' } & '
                            out += ' Web & '
                            for elem in line[-2]:
                                elem = f(elem)
                                out += f' {elem} &'
                            out = out[:-1] + '\\tabularnewline\\cline{6-14}\n' + ' &' * c + ' Flange & '
                            for elem in line[-1]:
                                elem = f(elem)
                                out += f' {elem} &'
                        elif s == -1:
                            for elem in line[:s]:
                                elem = f(elem)
                                c += 1
                                out += elem + ' & '
                            out += ' Web & '
                            for elem in line[-1]:
                                elem = f(elem)
                                out += f' {elem} &'
                    else:
                        if (type(line[1]) == str and 'Total' in line[1]) or (
                                type(line[0]) == str and 'Total' in line[0]):  # Stiffened Plate Data
                            _bold = True
                            out += '\\hline\n'
                        for elem in line:
                            elem = bold(f(elem)) if _bold else f(elem)
                            out += f' {elem} &'
                    out = out[:-1] + endl
                    if line[1] == 'Total St. Plate':  # Stiffened Plate Data
                        out = out[:-1] + '\\hline\n'
                elif type(line) == str:
                    out += '\\multicolumn{' + str(clmns) + '}{l}{' + line + '}' + endl
            return out

        # Sanity Check 
        for i in (self.Press_D, self.Plate_D, self.Stiff_D, self.St_Pl_D, self.PrimS_D):
            if len(i) == 0:
                Logger.error(('(classes.py) DataLogger.LaTeX_output(): Tabular data are not initialized.'
                         ' Consider using DataLogger.CreateTabularData First. Returning Nothing.'))
                return ''
        # Pressure Table
        clm_pres = 4 + len(self.conds)
        press_head = (
                '\\begin{longtable}{*{2}{>{\centering}m{1.5cm}}*{' + str(clm_pres - 2) + '}{>{\centering}m{2cm}}}\n'
                                                                                         '\\caption{Plating Pressure Data}\n'
                                                                                         '\\label{tab:Press_Data}\n'
                                                                                         '\\tabularnewline'
                                                                                         '\\hline\n')
        press_head += 'Name & Breadth [m] & CoA [m] (y,z) &'
        for i in self.conds: press_head += f' {i} [kN/$m^2$] &'
        press_head += ' Max Pressure [kN/$m^2$] ' + endl + '\\endfirsthead\n'
        press_tab = tabular(self.Press_D, clm_pres, press_head)
        press_tab += '\\end{longtable}\n\n'
        if Debug: print(press_tab)

        # Plating Table
        plate_head = ('\\begin{longtable}{*{4}{>{\centering}m{1.25cm}}*{8}{>{\centering}m{2cm}}}\n'
                    '\\caption{Plating Data}\n'
                    '\\label{tab:Plate_Data}\n'
                    '\\tabularnewline'
                    '\\hline\n'
                    'Name & Material & Effective Breadth [m] & Stiffener Spacing [mm] & CoA [m] (y,z) & Design Pressure [kN/$m^2$]'
                    '& Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm] & Corrosion Thickness [mm]'
                    '& Design Net Thickness [mm]& Design Net Thickness + 50\% Corrosion [mm] & As Built Thickness [mm] '+endl+'\\endfirsthead\n'
                    '\multicolumn{12}{c}{{\\bfseries \\tablename\\ \\thetable{} -- continued from previous page}}\\\\\\hline\n'
                    'Name & Material & Effective Breadth [m] & Stiffener Spacing [mm] & CoA [m] (y,z) & Design Pressure [kN/$m^2$]'
                    '& Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm] & Corrosion Thickness [mm]'
                    '& Design Net Thickness [mm]& Design Net Thickness + 50\% Corrosion [mm] & As Built Thickness [mm] '+endl+'\\endhead\n')
        plate_tab = tabular(self.Plate_D,12,plate_head)
        plate_tab += '\\end{longtable}\n\n'
        if Debug: print(plate_tab)

        # Stiffeners Table
        stiff_head =('\\begin{longtable}{*{6}{>{\centering}m{1.25cm}}*{8}{>{\centering}m{1.75cm}}}\n'
                    '\\caption{Stiffener Data}\n'
                    '\\label{tab:Stiff_Data}\n'
                    '\\tabularnewline'
                    '\\hline\n'
                    'Name & Material & Type & Z actual [$cm^3$] & Z rule [$cm^3$] &  &'
                    'Length [mm] & Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm] &'
                    'Buckling Net Thickness [mm] & Corrosion Thickness [mm] & Design Net Thickness [mm] '
                    '& Design Net Thickness + 50\% Corrosion [mm] & As Built Thickness [mm]'+endl+'\\endfirsthead\n'
                    '\multicolumn{14}{c}{{\\bfseries \\tablename\\ \\thetable{} -- continued from previous page}}\\\\\\hline\n'
                    'Name & Material & Type & Z actual [$cm^3$] & Z rule [$cm^3$] &  &'
                    'Length [mm] & Yield Net Thickness [mm] & Minimum Empirical Net Thickness [mm] &'
                    'Buckling Net Thickness [mm] & Corrosion Thickness [mm] & Design Net Thickness [mm] '
                    '& Design Net Thickness + 50\% Corrosion [mm] & As Built Thickness [mm]'+endl+'\\endhead\n')
        stiff_tab = tabular(self.Stiff_D,14,stiff_head)
        stiff_tab += '\\end{longtable}\n\n'
        if Debug: print(stiff_tab)

        # Stiffened Plate Table
        st_pl_head =('\\begin{longtable}{*{8}{>{\centering}m{1.72cm}}}\n'
                    '\\caption{Stiffened Plate Data}\n'
                    '\\label{tab:St_Pl_Data}\n'
                    '\\tabularnewline'
                    '\\hline\n'
                    'Name &  & Area n-50 [$mm^2$] '
                    '& CoA [m] (y,z) & Moments of Area [$cm^3$] '
                    '& ixx,c [$mm^4$] & $Area*(y_{c,\ element} - y_{c,\ st. plate})^2$ [$mm^4$] & ixx,pl [$mm^4$]'+endl+'\\endfirsthead\n'
                    '\multicolumn{8}{c}{{\\bfseries \\tablename\\ \\thetable{} -- continued from previous page}}\\\\\\hline\n'
                    'Name &  & Area n-50 [$mm^2$] '
                    '& CoA [m] (y,z) & Moments of Area [$cm^3$] '
                    '& ixx,c [$mm^4$] & $Area*(y_{c,\ element} - y_{c,\ st. plate})^2$ [$mm^4$] & ixx,pl [$mm^4$]'+endl+'\\endhead\n')
        st_pl_tab = tabular(self.St_Pl_D,8,st_pl_head)
        st_pl_tab += '\\end{longtable}\n\n'
        if Debug: print(st_pl_tab)

        # Ordinary Section Data
        or_se_head =('\\begin{longtable}{*{8}{>{\centering}m{1.72cm}}}\n'
                    '\\caption{Stiffened Plate Data}\n'
                    '\\label{tab:St_Pl_Data}\n'
                    '\\tabularnewline'
                    '\\hline\n'
                    'Name & Area n-50 [$mm^2$] '
                    '& CoA [m] (y,z) & Moments of Area [$cm^3$] '
                    '& Ixx,pc [$mm^4$] & $Area*(y_{CoA}-y_n)^2$ [$mm^4$] & Ixx [$mm^4$]'+endl+'\\endfirsthead\n'
                    '\multicolumn{8}{c}{{\\bfseries \\tablename\\ \\thetable{} -- continued from previous page}}\\\\\\hline\n'
                    'Name & Area n-50 [$mm^2$] '
                    '& CoA [m] (y,z) & Moments of Area [$cm^3$] '
                    '& Ixx,pc [$mm^4$] & $Area*(y_{CoA}-y_n)^2$ [$mm^4$] & Ixx [$mm^4$]'+endl+'\\endhead\n')
        or_se_tab = tabular(self.PrimS_D,8,or_se_head)
        or_se_tab += '\\end{longtable}\n\n'
        if Debug: print(or_se_tab)

        return press_tab, plate_tab, stiff_tab, st_pl_tab, or_se_tab
# end of file
