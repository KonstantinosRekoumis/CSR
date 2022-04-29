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
        if form=="fb":#flat bar
            pl = plate(root,(root[0]+math.cos(angle)*dimensions["lw"],root[1]+math.sin(angle)*dimensions["lw"]), dimensions["bw"], material)
            self.plates=()
        

        

