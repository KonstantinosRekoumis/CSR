import math
from modules.baseclass.block import Block
from modules.baseclass.subblocks.atm_sur_block import AtmSur
from modules.baseclass.subblocks.sea_sur_block import SeaSur
from modules.baseclass.stiff_plate import StiffPlate
from modules.utils.constants import LOADS
from modules.utils.decorators import auto_str
from modules.utils.logger import Logger


@auto_str
class Ship:
    """`Ship` The class-envelope of the entire design procedure.
    All the available data input to the programme are stored here.
    Args:
        LBP (float): The ship's Length Between Perpendiculars
        Lsc (float): The ship's Waterline Length @ Scantling Draught
        B (float): _description_
        T (float): _description_
        Tmin (float): _description_
        Tsc (float): _description_
        D (float): _description_
        Cb (float): _description_
        Cp (float): _description_
        Cm (float): _description_
        DWT (float): _description_
        stiff_plates (list[StiffPlate]): _description_
        blocks (list[Block]): _description_
    """
    def __init__(self,
                 LBP: float,
                 Lsc: float,
                 B: float,
                 T: float,
                 Tmin: float,
                 Tsc: float,
                 D: float,
                 Cb: float,
                 Cp: float,
                 Cm: float,
                 DWT: float,  # PSM_spacing,
                 stiff_plates: list[StiffPlate],
                 blocks: list[Block]):
        self.symmetrical = True  # Checks that implies symmetry. For the time being is arbitrary constant
        self.LBP = LBP
        self.Lsc = Lsc  # Rule Length
        self.B = B
        self.T = T
        self.Tmin = Tmin  # Minimum Draught at Ballast condition
        self.Tsc = Tsc  # Scantling Draught
        self.D = D
        self.Cb = Cb
        self.Cp = Cp
        self.Cm = Cm
        self.DWT = DWT
        # self.PSM_spacing = PSM_spacing
        self.Mwh = 0
        self.Mws = 0
        self.Msw_h_mid = 0
        self.Msw_s_mid = 0
        self.Cw = 0
        self.Cw_calc()
        self.moments_wave()
        self.moments_still()
        # Array to hold all of the stiffened plates
        self.stiff_plates = stiff_plates
        self.blocks = self.validate_blocks(blocks)
        self.evaluate_sea_n_air()
        [(i.get_coords(self.stiff_plates), i.CG.insert(0, self.Lsc / 2)) for i in
         self.blocks]  # bit of a cringe solution that saves time
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.Calculate_I(n50=True)
        self.kappa = 1.0  # material factor

        # Acceleration parameter Part 1 Chapter 4, Section 3 pp.180
        self.a0 = (1.58 - 0.47 * self.Cb) * (2.4 / math.sqrt(self.Lsc) + 34 / self.Lsc - 600 / self.Lsc ** 2)
        self.evaluate_kappa()

    def evaluate_kappa(self):
        """
        CSR Part 1 Chapter 3 Section 1.2.2.1 page 82
        Find the kappa factor by finding the density of material occurrence.
        Used after the stiff plates are loaded.
        """
        a = [0, 0, 0, 0]
        N = 0
        for plate in self.stiff_plates:
            if plate.tag == 6 or plate.null: continue
            if '32' in plate.plate.material:
                a[1] = a[1] + 1
            elif '36' in plate.plate.material:
                a[2] = a[2] + 1
            elif '40' in plate.plate.material:
                a[3] = a[3] + 1
            else:
                a[0] = a[0] + 1
            N += 1
        for i in range(len(a)):
            a[i] = a[i] / N
        self.kappa = a[0] * 1 + a[1] * 0.78 + a[2] * 0.72 + a[3] * 0.68

    def evaluate_beff(self):
        """
        To be used after corrosion addition evaluation. Plates have -1 mm initial corrosion.
        """
        [plate.L_eff() for plate in self.stiff_plates]  # b effective evaluation

    def validate_blocks(self, blocks: list[Block]):
        # The blocks are already constructed but we need to validate their responding plates' existence
        ids = [i.id for i in self.stiff_plates]
        for i in blocks:
            for j in i.list_plates_id:
                if (abs(j) not in ids):
                    Logger.error(
                        f"ship.validate_blocks: The block: {repr(i)} has as boundaries non-existent plates.Program Terminates")
                    quit()
            self.block_properties(i)
        return blocks

    def evaluate_sea_n_air(self):
        def atm_key(item: StiffPlate):
            return item.plate.start[0]

        shell_ = []
        deck_ = []
        for i in self.stiff_plates:
            if i.tag == 0 or i.tag == 4:
                shell_.append(i.id)
            elif i.tag == 5:
                deck_.append(i.id)
        self.blocks.append(SeaSur(shell_))
        self.blocks.append(AtmSur(deck_))

    def block_properties(self, block: Block):
        """
        Function built to give each block its contents properties\n
        For the time being the contents are static and case specific!\n
        In the Future maybe a more dynamic approach will be implemented.
        """

        if block.space_type in LOADS:
            block.payload = LOADS[block.space_type]
        elif block.space_type in ["SEA", "ATM"]:
            pass
        else:
            Logger.warning(
                '(classes.py) ship/block_properties: The Current block space type does not correspond to a specified '
                f'load.\n Check your input. Defaulting to type of VOID cargo for block : {str(block)}'
            )

    def Cw_calc(self):
        # CSR PART 1 CHAPTER 4.2
        if 300 >= self.Lsc >= 90:
            self.Cw = 10.75 - ((300 - self.Lsc) / 100) ** 1.5
        elif 350 >= self.Lsc >= 300:
            self.Cw = 10.75
        elif 500 >= self.Lsc >= 350:
            self.Cw = 10.75 - ((self.Lsc - 350) / 150) ** 1.5
        else:
            Logger.error("ship.Cw_Calc: The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()

    def moments_wave(self):
        """
        CSR PART 1 CHAPTER 4.3
        fm = {
            "<= 0" : 0.0,
            0.4 : 1.0,
            0.65: 1.0,
            ">= Lbp": 0.0
        }
        """
        self.Mws = -110 * self.Cw * self.LBP ** 2 * self.B * (self.Cb + 0.7) * 1e-3
        self.Mwh = 190 * self.Cw * self.LBP ** 2 * self.B * self.Cb * 1e-3

    def moments_still(self):
        """
        CSR PART 1 CHAPTER 4.2
        CSR page 187
        fsw = {
            "<= 0 " : 0.0,
            0.1  : 0.15,
            0.3 : 1.0,
            0.7 : 1.0,
            0.9 : 0.15,
            ">= Lbp" : 0
        }
        """
        self.Msw_h_mid = 171 * (self.Cb + 0.7) * self.Cw * self.LBP ** 2 * self.B * 1e-3 - self.Mwh
        self.Msw_s_mid = -0.85 * (171 * (self.Cb + 0.7) * self.Cw * self.LBP ** 2 * self.B * 1e-3 + self.Mws)

    def calc_CoA(self):
        area = 0
        MoM_x = 0
        MoM_y = 0

        for i in self.stiff_plates:
            if i.null: continue  # null plates are not to be taken for calculations
            area += i.n50_area
            MoM_x += i.n50_area * i.CoA[1]
            MoM_y += i.n50_area * i.CoA[0]

        if self.symmetrical:
            return MoM_x / area, MoM_y / area, area * 2

        return MoM_x / area, MoM_y / area, area

    def Calculate_I(self, n50):
        Ixx = 0
        Iyy = 0
        for i in self.stiff_plates:
            if i.null: continue  # null plates are not to be taken for calculations
            if n50:
                Ixx += i.n50_Ixx_c + (i.CoA[1] - self.yo) ** 2 * i.n50_area
                Iyy += i.n50_Iyy_c + (i.CoA[0] - self.xo) ** 2 * i.n50_area
            else:
                Ixx += i.Ixx_c + (i.CoA[1] - self.yo) ** 2 * i.area
                Iyy += i.Iyy_c + (i.CoA[0] - self.xo) ** 2 * i.area

        if self.symmetrical:
            return 2 * Ixx, 2 * Iyy

        return Ixx, Iyy

    def update(self, update_all=False):
        if update_all:
            [i.update() for i in self.stiff_plates]
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.Calculate_I(n50=True)

    def data_input(self, text):
        if "data" not in self.__dict__:
            self.data = text
        self.data += text

    def map_members(self):
        v = vars(self)
        v["kappa"] = f"{self.kappa: 0.3g}"
        v["Mwh"] = round(self.Mwh, 2)
        v["Mws"] = round(self.Mws, 2)
        v["Msw_h_mid"] = round(self.Msw_h_mid, 2)
        v["Msw_s_mid"] = round(self.Msw_s_mid, 2)
        v["Cw"] = round(self.Cw, 3)
        v["yo"] = round(self.yo, 3)
        v["Ixx"] = round(self.Ixx, 2)
        v["n50_Ixx"] = round(self.n50_Ixx, 2)
        v["a0"] = round(self.a0, 5)
        return v
