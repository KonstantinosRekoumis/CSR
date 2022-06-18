# #############################
''' Base classes to structure the code around them.
    As basic classes are chosen the plate class and the 
    stiffener class. Their fusion gives the stiffened plate class.
'''
# #############################
from utilities import c_error,c_warn
import matplotlib.pyplot as plt
import math
import numpy as np

# Global Parameters 
_PLACE_ = {
    "Shell":0,
    'InnerBottom':1,
    'Hopper':2,
    'Wing':3,
    'Bilge':4,
    'WeatherDeck':5,
    0:"Shell",
    1:'InnerBottom',
    2:'Hopper',
    3:'Wing',
    4:'Bilge',
    5:'WeatherDeck'
}

class plate():

    def __init__(self,start:tuple,end:tuple,thickness:float,material:str,tag:str):
        """
        The plate class is the bottom plate (no pun intended) class that is responsible for all geometry elements.
        Initializing a plate item requires the start and end point coordinates in meters, the plate's thickness in mm,
        and the plate's chosen material.
        """
        self.start = start
        self.end = end
        self.thickness = thickness*1e-3 #convert mm to m
        self.material = material
        try:
            self.tag = _PLACE_[tag]
        except KeyError:
            self.tag = _PLACE_["InnerBottom"] #Worst Case Scenario
            warn = self.__str__+"\nThe plate's original tag is non existent. The existing tags are:"
            c_warn(warn)
            [print(_PLACE_[i],") ->", i ) for i in _PLACE_ if type(i) == str]
            c_warn("The program defaults to Inner Bottom Plate")
        self.angle, self.length = self.calc_lna()
        self.area = self.length*self.thickness
        self.Ixx_c, self.Iyy_c = self.calc_I_center()
        self.CoA = self.calc_CoA()
    
    def __str__(self):
        if self.tag != 4:
            return f"PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {_PLACE_[self.tag]} "
        else: 
            return f"BILGE PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {_PLACE_[self.tag]} "

    def calc_lna(self):
        #calculate the plate's angle and length 
        dy = self.end[1]-self.start[1]
        dx = self.end[0]-self.start[0]
        try:
            a = math.atan2(dy,dx)
        except ZeroDivisionError:
            if dy > 0:
                a = math.pi/2
            elif dy <= 0:
                a = -math.pi/2 
        if self.tag != 4:
            l = math.sqrt(dy**2+dx**2)
        else :
            if abs(dx) == abs(dy):
                l = math.pi*abs(dx)/2
            else:
                c_error("-- ERROR --\n"+"Edit your design. As the only bilge type supported is quarter circle.")
                quit()
                
        return a,l

    def calc_I_center(self):
        ''' Calculate the plate's Moments of Inertia at the center of the plate'''
        b = self.thickness
        l = self.length
        a = self.angle
        if self.tag != 4:
            Ixx = b*l/12*((b*math.cos(a))**2+(l*math.sin(a))**2)
            Iyy = b*l/12*((b*math.cos(a+math.pi/2))**2+(l*math.sin(a+math.pi/2))**2)
        else:
            r = l/math.pi*2
            Ixx = 1/16*math.pi*(r**4-(r-self.thickness)**4)
            Iyy = 1/16*math.pi*(r**4-(r-self.thickness)**4)
            pass
        return Ixx, Iyy
    
    def calc_CoA(self):
        #calculates Center of Area relative to the Global (0,0)
        if self.tag != 4:
            return (self.start[0]+self.length/2*math.cos(self.angle)),(self.start[1]+self.length/2*math.sin(self.angle))
        else :
            r = self.length/math.pi*2
            if self.angle > 0 and self.angle < math.pi/2:
                startx = self.start[0]
                starty = self.end[1]
                return startx+(2*r/math.pi),starty-(2*r/math.pi)
            elif self.angle > 0 and self.angle < math.pi:
                startx = self.end[0]
                starty = self.start[1]
                return startx+(2*r/math.pi),starty+(2*r/math.pi)
            elif self.angle < 0 and self.angle > -math.pi/2:
                startx = self.end[0]
                starty = self.start[1]
                return startx-(2*r/math.pi),starty-(2*r/math.pi)
            elif self.angle < 0 and self.angle > -math.pi:
                startx = self.start[0]
                starty = self.end[1]
                return startx-(2*r/math.pi),starty+(2*r/math.pi)

    def render(self,r_m = "w"):
        """
        Rendering utility utilizing the matplotlib framework.
        r_m is the render mode. \'w\' stands for simple line plot
        It also returns a tuple containing significant geometrical properties. (meybe change later)
        """
        X,Y = self.render_data()[:2]
        if r_m == 'w':
            plt.plot(X,Y,color = "b")
        elif r_m == 'wb':
            marker = "."
            if self.tag == 4:
                marker = ''
            plt.plot(X,Y,color = "b",marker = marker)
        elif r_m == 'wC':
            marker = "."
            if self.tag == 4:
                marker = ''
            plt.plot(X,Y,color = "b",marker = marker)
            plt.plot(self.CoA[0],self.CoA[1],color = "red",marker = '+')

    def render_data(self):
        if self.tag != 4:
            out = [(self.start[0],self.end[0]),(self.start[1],self.end[1]), self.thickness,self.material,_PLACE_[self.tag]]
        else:
            if self.angle > 0 and self.angle < math.pi/2:
                start = -math.pi/2
                end = 0
                startx = self.start[0]
                starty = self.end[1]
            elif self.angle > 0 and self.angle < math.pi:
                start = 0
                end = math.pi/2
                startx = self.end[0]
                starty = self.start[1]
            elif self.angle < 0 and self.angle > -math.pi/2:
                start = -math.pi
                end = -math.pi/2
                startx = self.end[0]
                starty = self.start[1]
            elif self.angle < 0 and self.angle > -math.pi:
                start = math.pi/2
                end = math.pi
                startx = self.start[0]
                starty = self.end[1]
                
            lin = np.linspace(start,end,num = 10)
            r =  self.end[0]-self.start[0]
            X = startx+np.cos(lin)*abs(r)
            Y = starty+np.sin(lin)*abs(r)
            out = [X,Y, self.thickness,self.material,_PLACE_[self.tag]]

        return out

    def save_data(self):
        return [self.start,self.end,self.thickness,self.material,_PLACE_[self.tag]]

    def calc_I_global(self,axis = 'x'):
        ''' Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
            or an custom Vertical or Horizontal Axis as a dictionary
            ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)         '''
        if axis == 'x':
            #Default Global axis for the prime forces
            Ixx = self.Ixx_c + self.CoA[1]**2*self.area
            return Ixx
        elif axis == 'y':
            Iyy = self.Iyy_c + self.CoA[0]**2*self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis['axis'] == 'x':
                    Ixx = self.Ixx_c + (self.CoA[1]-axis["offset"])**2*self.area
                    return Ixx
                elif axis['axis'] == 'y':
                    Iyy = self.Iyy_c + (self.CoA[0]-axis["offset"])**2*self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print("The axis dictionary has no proper values.\n","axis :",axis['axis'],type(axis['axis']),"\noffset :",axis['offset'],type(axis['offset']))
                return None
            

class stiffener(): 
    ''' The stiffener class is a class derived from the plate class. Stiffener is consisted of or more plates.
    To create a stiffener insert its form as \'fb\' -> Flat Bars, \'g\' -> for angular beams, \'t\' for t beams and \'bb\' for bulbous bars.
    Dimensions are entered as a dictionary of keys \'lx\', \'bx\' x referring to web and\or flange length and thickness respectively.
    Material is to be inserted like in the plate class, while only the root coordinates are required.
    Angle is used to make the stiffener perpendicular relative to the supported plate's angle.'''
    def __init__(self,form:str,dimensions:dict,angle:float ,material:str, root:tuple[float], tag:str):
        # Support for only flat bars, T bars and angled bars
        # dimensions lw -> length, bw -> thickness
        self.type = form
        self.Ixx_c = 0
        self.Iyy_c = 0
        self.area = 0
        if self.type=="fb":#flat bar
            pw = plate(root,(root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3), dimensions["bw"], material,tag)
            self.plates = [pw]
        elif self.type=="g":#angled bar
            end_web = (root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3)
            pw = plate(root,end_web, dimensions["bw"], material,tag)
            end_flange = (end_web[0]+math.cos(angle)*dimensions["lf"]*1e-3,end_web[1]+math.sin(angle)*dimensions["lf"]*1e-3)
            pf = plate(end_web,end_flange,dimensions["bf"],material,tag)
            self.plates = [pw,pf]

        self.CoA,self.area = self.calc_CoA()
        self.calc_I()

    def calc_CoA(self):
        area = 0
        MoM_x = 0
        MoM_y = 0
        for i in self.plates:
            area += i.area
            MoM_x += i.area*i.CoA[0]
            MoM_y += i.area*i.CoA[1]
        
        return (MoM_x/area,MoM_y/area) , area
    
    def calc_I(self):
        Ixx = 0
        Iyy = 0

        for i in self.plates:
            Ixx += i.calc_I_global({'axis': 'x','offset': self.CoA[1]})
            Iyy += i.calc_I_global({'axis': 'y','offset': self.CoA[0]})

        self.Ixx_c = Ixx
        self.Iyy_c = Iyy

    def calc_I_global(self,axis = 'x'):
        ''' Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
            or an custom Vertical or Horizontal Axis as a dictionary
            ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)         '''
        if axis == 'x':
            #Default Global axis for the prime forces
            Ixx = self.Ixx_c + self.CoA[1]**2*self.area
            return Ixx
        elif axis == 'y':
            Iyy = self.Iyy_c + self.CoA[0]**2*self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis['axis'] == 'x':
                    Ixx = self.Ixx_c + (self.CoA[1]-axis["offset"])**2*self.area
                    return Ixx
                elif axis['axis'] == 'y':
                    Iyy = self.Iyy_c + (self.CoA[0]-axis["offset"])**2*self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print("The axis dictionary has no proper values.\n","axis :",axis['axis'],type(axis['axis']),"\noffset :",axis['offset'],type(axis['offset']))
                return None

    def render(self,r_m = 'w'):

        for i in self.plates:
            i.render()
    
    def render_data(self):
        X = []
        Y = []
        T = []
        M = []
        for i in self.plates:
            tmp = i.render_data()
            X.append(tmp[0])
            Y.append(tmp[1])
            T.append(tmp[2])
            M.append(tmp[3])
        
        return X,Y,T,M

class stiff_plate():
    def __init__(self,id:int,plate:plate, spacing:float,l_pad:float,r_pad:float, stiffener_:dict ):
        """
        The stiff_plate class is the Union of the plate and the stiffener(s).
        Its args are :
        plate -> A plate object
        spacing -> A float number, to express the distance between two stiffeners in mm.
        l_pad, r_pad -> Float numbers, to express the padding distance (in mm) of the stiffeners with respect to the left and right 
                        edge of the base plate.
        stiffener_dict -> A dict containing data to create stiffeners : {type : str, dims : [float (in mm)],mat:str}
        Spacing is in mm.
        """
        self.id = id
        self.plate = plate
        self.tag = plate.tag #it doesn't make sense not too grab it here
        self.stiffeners = []
        self.spacing = spacing*1e-3 
        self.l_pad = l_pad*1e-3
        self.r_pad = r_pad*1e-3
        if self.plate.tag != 4:
            net_l = self.plate.length - self.l_pad - self.r_pad
            N = math.floor(net_l/self.spacing)
            for i in range(1,N):
                root = (self.plate.start[0]+math.cos(self.plate.angle)*(self.spacing*i+self.l_pad),self.plate.start[1]+math.sin(self.plate.angle)*(self.spacing*i+self.l_pad))
                self.stiffeners.append(stiffener(stiffener_['type'],stiffener_['dimensions'],self.plate.angle,stiffener_['material'],root,plate.tag)) 
        self.CoA , self.area = self.CenterOfArea()
        self.Ixx, self.Iyy = self.calc_I()

    def CenterOfArea(self):
        total_A = self.plate.area 
        total_Mx = self.plate.area*self.plate.CoA[1]
        total_My = self.plate.area*self.plate.CoA[0]
        if len(self.stiffeners) != 0:
            for i in self.stiffeners:
                total_A += i.area
                total_Mx += i.area*i.CoA[1]
                total_My += i.area*i.CoA[0]
        
        return (total_Mx/total_A,total_My/total_A) , total_A
    
    def calc_I (self):
        Ixx = self.plate.calc_I_global({'axis': 'x','offset': self.CoA[1]})
        Iyy = self.plate.calc_I_global({'axis': 'y','offset': self.CoA[0]})

        if len(self.stiffeners) != 0:
            for i in self.stiffeners:
                Ixx += i.calc_I_global({'axis': 'x','offset': self.CoA[1]})
                Iyy += i.calc_I_global({'axis': 'y','offset': self.CoA[0]})

        return Ixx, Iyy
    def render(self,r_m='w_b'):
        plt.axis('square')
        self.plate.render(r_m=r_m)
        [i.render() for i in self.stiffeners]

class long_stiff_plate():
    def __init__(self,stiff_plates: list[stiff_plate],girders:list[plate]):
        '''
        The long_stiff_plate class exists to enwrap the cases where we want to create a longer 
        stiffened plate with girders.
        As arguments it requires :
        stiff_plates -> A list containing the stiffened plates that consist the long plate
        girders -> A list containing the long plate's girders,even if girders is empty the
                   constructor introduces

        '''
        pass
    # TO COMPLETE

class block():
    """
    Block class can be usefull to evaluate the plates that consist a part of the Midship Section, ie. a Water Ballast tank, or Cargo Space.
    This is done to further enhance the clarity of what substances are in contact with certain plates.
    Currently are supported 5 Volume Categories :
    1) Water Ballast -> type : WB
    2) Dry Cargo -> type: DC
    3) Fuel Oil/ Lube Oil/ Diesel Oil -> type: OIL
    4) Fresh Water -> type: FW
    5) Dry/Void Space -> type: VOID
    """

    def __init__(self,space_type:str, list_plates_id : list[int],*args):
        TAGS = ['WB','DC','OIL','FW','VOID']
        """
        We need to pass the type of Cargo that is stored in the Volume and out of which stiffened plates it consists of
        """
        if space_type in TAGS:
            self.space_type = space_type
        else:
            c_error("The block type is not currently supported or non-existent.")
        self.list_plates_id = list_plates_id
    
    def __str__(self):
        return f"BLOCK: type:{self.space_type}, ids: {self.list_plates_id}"

class ship():

    def __init__(self, LBP:int, B, T, D, Cb, Cp, Cm, DWT, stiff_plates:list[stiff_plate],blocks:list[block]):
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
        #Array to hold all of the stiffened plates
        self.stiff_plates = stiff_plates
        self.blocks = self.validate_blocks(blocks)
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I()

    def validate_blocks(self,blocks :list[block]):
        # The blocks are already constructed but we need to validate their responding plates' existence
        ids = [i.id for i in self.stiff_plates]
        for i in blocks:
            for j in i.list_plates_id:
                if j not in ids:
                    c_error(f"The block: {i} has as boundaries non-existent plates.Program Terminates")
                    quit()
        return blocks


    def Moments_wave(self):
        # CSR PART 1 CHAPTER 4.3
        if self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((300-self.LBP)/100)**1.5
        elif self.LBP <= 350 and self.LBP >= 300: 
            C1 = 10.75
        elif self.LBP <= 500 and self.LBP >= 350: 
            C1 = 10.75-((self.LBP-350)/150)**1.5
        else:
            c_warn("The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()

        self.Mws = -110*C1*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        self.Mwh =  190*C1*self.LBP**2*self.B*self.Cb*1e-3

    def Moments_still(self):
        # CSR PART 1 CHAPTER 4.2
        if self.LBP <= 300 and self.LBP >= 90: 
            C1 = 10.75-((300-self.LBP)/100)**1.5
        elif self.LBP <= 350 and self.LBP >= 300: 
            C1 = 10.75
        elif self.LBP <= 500 and self.LBP >= 350: 
            C1 = 10.75-((self.LBP-350)/150)**1.5
        else:
            c_warn("The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()
        # Legacy calc
        # self.Msw_h_mid = (171*((self.Cb+0.7)-190*self.Cb))*C1*self.LBP**2*self.B*1e-3
        # self.Msw_s_mid =  -51.85*C1*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        # CSR page 187
        self.Msw_h_mid = 171*(self.Cb+0.7)*C1*self.LBP**2*self.B*1e-3 - self.Mwh
        self.Msw_s_mid = -0.85*(171*(self.Cb+0.7)*C1*self.LBP**2*self.B*1e-3 + self.Mws)

    def calc_CoA(self):
        area  = 0 
        MoM_x = 0 
        MoM_y = 0

        for i in self.stiff_plates:
            area += i.area
            MoM_x += i.area*i.CoA[1]
            MoM_y += i.area*i.CoA[0]

        return MoM_x/area, MoM_y/area, area

    def Calculate_I(self):
        Ixx = 0
        Iyy = 0
        for i in self.stiff_plates:
            Ixx += i.Ixx + (i.CoA[1]-self.yo)**2*i.area
            Iyy += i.Iyy + (i.CoA[0]-self.xo)**2*i.area

        return Ixx, Iyy        
    def render(self,r_m='w'):
        fig = plt.figure()
        for i in self.stiff_plates:
            i.render(r_m=r_m)
        # plt.axis([-1,self.B/2+1,-1,self.D+3])
        plt.show()