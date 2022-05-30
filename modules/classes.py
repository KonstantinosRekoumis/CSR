# #############################
''' Base classes to structure the code around them.
    As basic classes are chosen the plate class and the 
    stiffener class. Their fusion gives the stiffened plate class.
'''
# #############################
import matplotlib.pyplot as plt
import math

class plate():

    def __init__(self,start:tuple,end:tuple,thickness:float,material:str):
        """
        The plate class is the bottom plate (no pun intended) class that is responsible for all geometry elements.
        Initializing a plate item requires the start and end point coordinates in meters, the plate's thickness in mm,
        and the plate's chosen material.
        """
        self.start = start
        self.end = end
        self.thickness = thickness*1e-3
        self.material = material
        self.angle, self.length = self.calc_lna()
        self.area = self.length*self.thickness
        self.Ixx_c, self.Iyy_c = self.calc_I_center()
        self.CoA = self.calc_CoA()

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
    
    def calc_CoA(self):
        #calculates Center of Area relative to the Global (0,0)
        return (min((self.start[0],self.end[0]))+self.length/2*math.cos(self.angle)),(min((self.start[1],self.end[1]))+self.length/2*math.sin(self.angle))

    def render(self,r_m = "w"):
        """
        Rendering utility utilizing the matplotlib framework.
        r_m is the render mode. \'w\' stands for simple line plot
        It also returns a tuple containing significant geometrical properties. (meybe change later)
        """
        if r_m == 'w':
            plt.plot((self.start[0], self.end[0]),(self.start[1], self.end[1]),color = "b")
        elif r_m == 'wb':
            plt.plot((self.start[0], self.end[0]),(self.start[1], self.end[1]),color = "b",marker = 3)

        out = [(self.start[0], self.end[0]),(self.start[1], self.end[1]), self.thickness,self.material]
        return out


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
    def __init__(self,form:str,dimensions:dict,angle:float ,material:str, root:tuple[float]):
        # Support for only flat bars, T bars and angled bars
        # dimensions lw -> length, bw -> thickness
        self.type = form
        self.Ixx_c = 0
        self.Iyy_c = 0
        self.area = 0
        if self.type=="fb":#flat bar
            pw = plate(root,(root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3), dimensions["bw"], material)
            self.plates = [pw]
        elif self.type=="g":#angled bar
            end_web = (root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3)
            pw = plate(root,end_web, dimensions["bw"], material)
            end_flange = (end_web[0]+math.cos(angle)*dimensions["lf"]*1e-3,end_web[1]+math.sin(angle)*dimensions["lf"]*1e-3)
            pf = plate(end_web,end_flange,dimensions["bf"],material)
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

        


class stiff_plate():

    def __init__(self, plate:plate, spacing:float, stiffener_:dict ):
        """
        Spacing is in mm.
        """
        self.plate = plate
        self.stiffeners = []
        self.spacing = spacing*1e-3 
        N = math.floor(self.plate.length/self.spacing)
        for i in range(1,N):
            root = (self.plate.start[0]+math.cos(self.plate.angle)*self.spacing*i,self.plate.start[1]+math.sin(self.plate.angle)*self.spacing*i)
            self.stiffeners.append(stiffener(stiffener_['type'],stiffener_['dimensions'],self.plate.angle,stiffener_['material'],root)) 

        self.CoA , self.area = self.CenterOfArea()
        self.Ixx, self.Iyy = self.calc_I()

    def CenterOfArea(self):
        total_A = self.plate.area 
        total_Mx = self.plate.area*self.plate.CoA[1]
        total_My = self.plate.area*self.plate.CoA[0]
        for i in self.stiffeners:
            total_A += i.area
            total_Mx += i.area*i.CoA[1]
            total_My += i.area*i.CoA[0]
        
        return (total_Mx/total_A,total_My/total_A) , total_A
    
    def calc_I (self):
        Ixx = self.plate.calc_I_global({'axis': 'x','offset': self.CoA[1]})
        Iyy = self.plate.calc_I_global({'axis': 'y','offset': self.CoA[0]})

        for i in self.stiffeners:
            Ixx += i.calc_I_global({'axis': 'x','offset': self.CoA[1]})
            Iyy += i.calc_I_global({'axis': 'y','offset': self.CoA[0]})

        return Ixx, Iyy
    def render(self):
        plt.axis('square')
        self.plate.render(r_m='wb')
        [i.render() for i in self.stiffeners]
        # self.CoA = self.plate.area*shhhhhhhhh



class ship():

    def __init__(self, LBP:int, B, T, D, Cb, Cp, Cm, DWT, stiff_plates:list[stiff_plate]):
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
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I()


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
    def render(self):
        fig = plt.figure()
        for i in self.stiff_plates:
            i.render()
        plt.axis([-1,self.B/2+1,-1,self.D+3])
        plt.show()
