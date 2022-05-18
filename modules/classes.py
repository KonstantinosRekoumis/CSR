# #############################
''' Base classes to structure the code around them.
    As basic classes are chosen the plate class and the 
    sitffener class. Their fusion gives the stiffened plate class.
'''
# #############################
import math
import rules as rl

class plate():

    def __init__(self,start:tuple,end:tuple,thickness:float,material:str):
        self.start = start
        self.end = end
        self.thickness = thickness
        self.meterial = material
        tmp = self.calc_lna()
        self.angle = tmp[0]
        self.length = tmp[1]
        self.area = self.length*self.thickness
        tmp = self.calc_I_center()
        self.Ixx_c = tmp[0]
        self.Iyy_c = tmp[1]

    def calc_lna(self):
        #calculate the plate's angle and length 
        dy = self.end[1]-self.start[1]
        dx = self.end[0]-self.start[0]
        a = math.atan(dy/dx)
        l = math.sqrt(dy**2+dx**2)
        return a,l

    def calc_I_center(self):
        ''' Calculate the plate's Moments of Inertia at the center of the plate'''
        b = self.thickness
        l = self.length
        a = self.angle
        Ixx = b*l/12*((b*math.cos(a))**2+(l*math.sin(a))**2)
        Iyy = b*l/12*((b*math.cos(a+math.pi/2))**2+(l*math.sin(a+math.pi/2))**2)
        return Ixx, Iyy

    def calc_I_global(self,axis = 'x'):
        ''' Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
            or an custom Vertical or Horizontal Axis as a dictionary
            ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)         '''
        if axis == 'x':
            #Default Global axis for the prime forces
            Ixx = self.Ixx_c + (min((self.start[1],self.end[1]))+self.length/2*math.sin(self.angle))**2*self.area
            return Ixx
        elif axis == 'y':
            Iyy = self.Iyy_c + (min((self.start[0],self.end[0]))+self.length/2*math.sin(self.angle-math.pi/4))**2*self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis['axis'] == 'x':
                    Ixx = self.Ixx_c + (min((self.start[1],self.end[1]))+self.length/2*math.sin(self.angle)-axis["offset"])**2*self.area
                    return Ixx
                elif axis['axis'] == 'y':
                    Iyy = self.Iyy_c + (min((self.start[0],self.end[0]))+self.length/2*math.sin(self.angle-math.pi/2)-axis["offset"])**2*self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print("The axis dictionary has no proper values.\n","axis :",axis['axis'],type(axis['axis']),"\noffset :",axis['offset'],type(axis['offset']))
                return None
            

class stiffener(): 
    ''' The stiffener class is child class of the plate's class. It is 
    consisted out of one to three plates '''
    def __init__(self,form:str,dimensions:dict,angle:float,material:str):
        #Support for only flat bars, T bars and angled bars
        # if form=="fb":#flat bar
        #     pl = plate(root,(root[0]+math.cos(angle)*dimensions["lw"],root[1]+math.sin(angle)*dimensions["lw"]), dimensions["bw"], material)
        #     self.plates=()
        print("SCAMMED")


class ship():

    def __init__(self, LBP, B, T, D, Cb, Cp, Cm, DWT):
        self.LBP = LBP
        self.B  = B
        self.T = T
        self.D = D
        self.Cb = Cb
        self.Cp = Cp
        self.Cm = Cm
        self.DWT = DWT
        self.Mwh = 0
        self.Mws = 0
        self.Msw_h_mid = 0
        self.Msw_s_mid = 0
        self.Moments_wave()
        self.Moments_still()
        pass 

    def Moments_wave(self):
        # CSR PART 1 CHAPTER 4.3
        if self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((300-self.LBP)/100)**1.5
        elif self.LBP <= 350 and self.LBP >= 300: 
            C1 = 10.75
        elif self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((self.LBP-350)/150)**1.5
        else:
            print("The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()

        self.Mws = -110*C1*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        self.Mwh =  190*C1*self.LBP**2*self.B*self.Cb*1e-3

    def Moments_still(self):
        # CSR PART 1 CHAPTER 4.2
        if self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((300-self.LBP)/100)**1.5
        elif self.LBP <= 350 and self.LBP >= 300: 
            C1 = 10.75
        elif self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((self.LBP-350)/150)**1.5
        else:
            print("The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()
        # Legacy calc
        # self.Msw_h_mid = (171*((self.Cb+0.7)-190*self.Cb))*C1*self.LBP**2*self.B*1e-3
        # self.Msw_s_mid =  -51.85*C1*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        # CSR page 187
        self.Msw_h_mid = 171*(self.Cb+0.7)*C1*self.LBP**2*self.B*1e-3 - self.Mwh
        self.Msw_s_mid = -0.85*(171*(self.Cb+0.7)*C1*self.LBP**2*self.B*1e-3 + self.Mws)


