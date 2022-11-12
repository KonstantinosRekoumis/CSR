# #############################
''' Base classes to structure the code around them.
    As basic classes are chosen the plate class and the 
    stiffener class. Their fusion gives the stiffened plate class.
'''
# #############################
from modules.constants import LOADS
from modules.utilities import c_error, c_info,c_warn, d2r,linespace
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
def normals2D(geom,flip_n = False):
    eta = [[None,None]]*len(geom)
    for i in range(len(geom)-1):
        xba = geom[i+1][0]-geom[i][0]
        yba = geom[i+1][1]-geom[i][1]
        if flip_n:
            yba = - yba
            xba = - xba
        nrm2 = np.sqrt(yba**2+xba**2)
        if nrm2 == 0:
            eta[i][0] = yba/nrm2
            eta[i][1] = -xba/nrm2
            c_warn(f"eta = {eta}, norm = {nrm2}, geom = {geom}")
        else:
            eta[i][0] = yba/nrm2
            eta[i][1] = -xba/nrm2
    # last point (a somewhat simplistic approach)
    eta[-1] = eta[-2]    
    return eta

class plate():

    def __init__(
                self,start:tuple,end:tuple,
                thickness:float,material:str,
                tag:str):
        """
        The plate class is the bottom plate (no pun intended) class that is responsible for all geometry elements.
        Initializing a plate item requires the start and end point coordinates in meters, the plate's thickness in mm,
        and the plate's chosen material.
        """
        self.start = start
        self.end = end
        self.thickness = thickness*1e-3 #convert mm to m
        self.net_thickness = self.thickness
        self.cor_thickness = -1e-3
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
        self.Ixx_c, self.Iyy_c = self.calc_I_center(b = self.net_thickness)
        self.CoA = self.calc_CoA()
        self.eta = self.eta_eval()
        #t = net + 50% corrosion Related Calculations and Quantities
        self.n50_thickness = self.net_thickness + 0.5*self.cor_thickness
        self.n50_area = self.length*self.n50_thickness
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I_center(b=self.n50_thickness)
    
    def __str__(self):
        if self.tag != 4:
            return f"PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "
        else: 
            return f"BILGE PLATE: @[{self.start},{self.end}], material: {self.material}, thickness: {self.thickness}, tag: {self.tag} ({_PLACE_[self.tag]}) "

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

    def calc_I_center(self, b):
        ''' Calculate the plate's Moments of Inertia at the center of the plate'''
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
            if self.angle > 0 and self.angle < math.pi/2: # 1st quarter
                startx = self.start[0]
                starty = self.end[1]
                return startx+(2*r/math.pi),starty-(2*r/math.pi) 
            elif self.angle > 0 and self.angle < math.pi: #2nd quarter
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
        return [self.start,self.end,self.thickness*1e3,self.material,_PLACE_[self.tag]]

    def calc_I_global(self, Ixx_c, Iyy_c, axis = 'x'):
        ''' Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
            or an custom Vertical or Horizontal Axis as a dictionary
            ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)         '''
        if axis == 'x':
            #Default Global axis for the prime forces
            Ixx = Ixx_c + self.CoA[1]**2*self.area
            return Ixx
        elif axis == 'y':
            Iyy = Iyy_c + self.CoA[0]**2*self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis['axis'] == 'x':
                    Ixx = Ixx_c + (self.CoA[1]-axis["offset"])**2*self.area
                    return Ixx
                elif axis['axis'] == 'y':
                    Iyy = Iyy_c + (self.CoA[0]-axis["offset"])**2*self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print("The axis dictionary has no proper values.\n","axis :",axis['axis'],
                        type(axis['axis']),"\noffset :",axis['offset'],type(axis['offset']))
                return None
    
    def eta_eval(self):
        ''' Evaluates the normal vectors of the plate face. Useful in Pressure offloading'''
        X,Y = self.render_data()[:2]
        geom = [[X[i],Y[i]] for i in range(len(X))]
        return normals2D(geom)
    def update(self):
        self.thickness = self.net_thickness+self.cor_thickness
        # self.angle, self.length = self.calc_lna() # They are not supposed to change for the time being
        self.area = self.length*self.thickness
        self.Ixx_c, self.Iyy_c = self.calc_I_center(b=self.net_thickness)
        self.CoA = self.calc_CoA()
        self.eta = self.eta_eval()
        self.n50_thickness = self.net_thickness + 0.5*self.cor_thickness
        self.n50_area = self.length*self.n50_thickness
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I_center(b=self.n50_thickness)
    def Debug(self):
        print ('start : ',self.start)
        print ('end : ',self.end)
        print ('thickness : ',self.thickness)
        print ('net_thickness : ',self.net_thickness)
        print ('cor_thickness : ',self.cor_thickness)
        print ('material : ',self.material)

        print('self.angle : ',self.angle)        
        print('self.length : ',self.length)
        print('self.area : ',self.area)
        print('self.Ixx_c : ',self.Ixx_c)        
        print('self.Iyy_c : ',self.Iyy_c)
        print('self.CoA : ',self.CoA)
        print('self.eta : ',self.eta)
        print('self.n50_thickness : ',self.n50_thickness)
        print('self.n50_area : ',self.n50_area)
        print('self.n50_Ixx_c : ',self.n50_Ixx_c)


class stiffener(): 
    ''' The stiffener class is a class derived from the plate class. Stiffener is consisted of or more plates.
    To create a stiffener insert its form as \'fb\' -> Flat Bars, \'g\' -> for angular beams, \'t\' for t beams and \'bb\' for bulbous bars.
    Dimensions are entered as a dictionary of keys \'lx\', \'bx\' x referring to web and\or flange length and thickness respectively.
    Material is to be inserted like in the plate class, while only the root coordinates are required.
    Angle is used to make the stiffener perpendicular relative to the supported plate's angle.'''
    def __init__(
                self,form:str,dimensions:dict, angle:float, root:tuple[float],
                material:str, tag:str):
        # Support for only flat bars, T bars and angled bars
        # dimensions lw -> length, bw -> thickness
        self.type = form
        self.material = material
        self.Ixx_c = 0
        self.Iyy_c = 0
        self.area = 0
        # n50
        self.n50_area = 0
        self.n50_Ixx_c = 0
        self.n50_Iyy_c = 0
        self.dimensions = dimensions
        if self.type=="fb":#flat bar
            pw = plate(root,
                        (root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,
                        root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3),
                        dimensions["bw"], material,tag)
            self.plates = [pw]
        elif self.type=="g":#angled bar
            end_web = (root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,
                        root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3)
            pw = plate(root,end_web, dimensions["bw"], material,tag)
            end_flange = (end_web[0]+math.cos(angle)*dimensions["lf"]*1e-3,
                            end_web[1]+math.sin(angle)*dimensions["lf"]*1e-3)
            pf = plate(end_web,end_flange,dimensions["bf"],material,tag)
            self.plates = [pw,pf]
        elif self.type=="tb":# T bar
            end_web = (root[0]+math.cos(angle+math.pi/2)*dimensions["lw"]*1e-3,
                        root[1]+math.sin(angle+math.pi/2)*dimensions["lw"]*1e-3)
            pw = plate(root,end_web, dimensions["bw"], material,tag)
            start_flange = (end_web[0]-math.cos(angle)*dimensions["lf"]/2*1e-3,
                            end_web[1]-math.sin(angle)*dimensions["lf"]/2*1e-3)
            end_flange = (end_web[0]+math.cos(angle)*dimensions["lf"]/2*1e-3,
                            end_web[1]+math.sin(angle)*dimensions["lf"]/2*1e-3)
            pf = plate(start_flange,end_flange,dimensions["bf"],material,tag)
            self.plates = [pw,pf]
        

        self.calc_CoA()
        self.calc_I()
    def __repr__(self) -> str:
        dim = '{'
        for i,plate in enumerate(self.plates):
            if i == 0:
                dim += f"\'lw\':{plate.length*1e3},\'bw\':{plate.thickness*1e3}"
            else:
                dim += f",\'l{i}\':{plate.length*1e3},\'b{i}\':{plate.thickness*1e3}"

        return f'stiffener(type: {self.type},dimensions : {dim}'+'}'

    def calc_CoA(self):
        area = 0
        n50_area = 0
        MoM_x = 0
        MoM_y = 0
        for i in self.plates:
            area += i.area
            n50_area += i.n50_area
            MoM_x += i.area*i.CoA[0]
            MoM_y += i.area*i.CoA[1]
        self.CoA=(MoM_x/area,MoM_y/area)
        self.area=area
        self.n50_area=n50_area 
    
    def calc_I(self):
        Ixx = 0
        Iyy = 0
        n50_Ixx = 0
        n50_Iyy = 0

        for i in self.plates:
            Ixx += i.calc_I_global(i.Ixx_c,i.Iyy_c,{'axis': 'x','offset': self.CoA[1]})
            n50_Ixx += i.calc_I_global(i.n50_Ixx_c,i.n50_Iyy_c,{'axis': 'x','offset': self.CoA[1]})
            Iyy += i.calc_I_global(i.Ixx_c,i.Iyy_c,{'axis': 'y','offset': self.CoA[0]})
            n50_Iyy += i.calc_I_global(i.n50_Ixx_c,i.n50_Iyy_c,{'axis': 'y','offset': self.CoA[0]})

        self.Ixx_c = Ixx
        self.Iyy_c = Iyy
        self.n50_Ixx_c = n50_Ixx
        self.n50_Iyy_c = n50_Iyy

    def calc_I_global(self,Ixx_c,Iyy_c,axis = 'x'):
        ''' Calculate the moments relative to an axis. The axis argument is either passed as an string 'x' or 'y'(to indicate the Global Axis)
            or an custom Vertical or Horizontal Axis as a dictionary
            ie. axis = { 'axis' : 'x', 'offset' : 1.0} (This indicates an horizontal axis offset to the global axis positive 1 unit.)         '''
        if axis == 'x':
            #Default Global axis for the prime forces
            Ixx = Ixx_c + self.CoA[1]**2*self.area
            return Ixx
        elif axis == 'y':
            Iyy = Iyy_c + self.CoA[0]**2*self.area
            return Iyy
        elif type(axis) == dict:
            try:
                if axis['axis'] == 'x':
                    Ixx = Ixx_c + (self.CoA[1]-axis["offset"])**2*self.area
                    return Ixx
                elif axis['axis'] == 'y':
                    Iyy = Iyy_c + (self.CoA[0]-axis["offset"])**2*self.area
                    return Iyy
            except KeyError:
                print("The axis dictionary is not properly structured")
                return None
            except TypeError:
                print("The axis dictionary has no proper values.\n","axis :",axis['axis'],type(axis['axis']),"\noffset :",axis['offset'],type(axis['offset']))
                return None

    def calc_Z(self,Ixx,Iyy):
        max_r = 0
        max_point = []
        for plate in self.plates:
            rs = math.sqrt((plate.start[0]-self.CoA[0])**2+(plate.start[1]-self.CoA[1])**2)
            re = math.sqrt((plate.end[0]-self.CoA[0])**2+(plate.end[1]-self.CoA[1])**2)
            if max_r<rs: 
                max_r = rs 
                max_point = plate.start
            elif max_r<re:
                max_r = re
                max_point = plate.end
            Zxx = Ixx/abs(max_point[1]-self.CoA[1]) if abs(max_point[1]-self.CoA[1])!=0 else Ixx/abs(self.plates[0].thickness)
            Zyy = Iyy/abs(max_point[0]-self.CoA[0]) if abs(max_point[0]-self.CoA[0])!=0 else Ixx/abs(self.plates[0].thickness)
        return Zxx,Zyy 


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
    def update(self):
        for plate in self.plates:
            plate.update()
        self.calc_CoA()
        self.calc_I()

class stiff_plate():
    def __init__(
                self,id:int,plate:plate, spacing:float, l_pad:float, r_pad:float,
                stiffener_:dict, skip :int, null:bool= False ):
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
        self.tag = plate.tag #it doesn't make sense not to grab it here
        self.stiffeners = []
        self.spacing = spacing*1e-3 
        self.l_pad = l_pad*1e-3
        self.r_pad = r_pad*1e-3
        self.skip = skip
        self.null = null
        if self.plate.tag != 4 and not self.null:
            net_l = self.plate.length - self.l_pad - self.r_pad
            N = math.floor(net_l/self.spacing)
            _range = linespace(1,N,1,skip=skip)
            for i in _range:
                root = (self.plate.start[0]+math.cos(self.plate.angle)*(self.spacing*i+self.l_pad),
                        self.plate.start[1]+math.sin(self.plate.angle)*(self.spacing*i+self.l_pad))
                self.stiffeners.append(stiffener(
                                                stiffener_['type'],stiffener_['dimensions'],
                                                self.plate.angle,root,stiffener_['material'],
                                                plate.tag)) 
        self.CoA = []
        self.area = 0
        self.n50_area = 0
        self.CenterOfArea()
        self.Ixx_c, self.Iyy_c = self.calc_I(n50=False)
        self.n50_Ixx_c, self.n50_Iyy_c = self.calc_I(n50=True)
        self.Pressure = {}
        #renew stiffener

    def b_eff(self,PSM_spacing):
        if len(self.stiffeners)!=0:
            bef = min( self.spacing, PSM_spacing*200)
            if self.plate.net_thickness < 8*1e-3 : bef = max(0.6,bef)
            self.plate.length = len(self.stiffeners)*bef
            self.update()

    def LaTeX_output(self):
        if self.null:return ('','')
        def _round(tp:tuple, dig:int):
            out = []
            for i in tp:
                out.append(round(i,dig))
            return tuple(out)
        V = {
            'fb':'Flat Bar',
            'g' :'Angled Bar',
            'tb':'T Bar'
        }

        out_plate = (
            f'Plate {self.id} & '
            f' {self.plate.material} & '
            f' {round(self.plate.length,3)} & '
            f' {round(self.spacing*1e3,2)} & '
            f' {_round(self.CoA,3)} & '
            f' {round(self.plate.thickness*1e3,2)} & '
            f' {round(self.plate.net_thickness*1e3,2)} & '
            f' {round(self.plate.cor_thickness*1e3,2)} '
            '\\tabularnewline \\hline\n')
        if len(self.stiffeners) != 0:
            out_stif = (
                ' Web &'
                f' {self.stiffeners[0].plates[0].material} & '
                f' {round(self.stiffeners[0].plates[0].length*1e3,2)} & '
                f' {round(self.stiffeners[0].plates[0].thickness*1e3,2)} & '
                f' {round(self.stiffeners[0].plates[0].net_thickness*1e3,2)} & '
                f' {round(self.stiffeners[0].plates[0].cor_thickness*1e3,2)}  '
            )
            if len(self.stiffeners[0].plates) == 2:
                out_stif += (
                    '\\tabularnewline \\cline{3-8}\n & & Flange &'
                    f' {self.stiffeners[0].plates[0].material} & '
                    f' {round(self.stiffeners[0].plates[1].length*1e3,2)} & '
                    f' {round(self.stiffeners[0].plates[1].thickness*1e3,2)} & '
                    f' {round(self.stiffeners[0].plates[1].net_thickness*1e3,2)} & '
                    f' {round(self.stiffeners[0].plates[1].cor_thickness*1e3,2)}  '
                )
                out_stif = ('\\multirow{2}{*}{'+f'Plate {self.id}'+'} & '
                            '\\multirow{2}{*}{'+V[self.stiffeners[0].type]+'} & ' + out_stif)
            else:
                out_stif = f'Plate {self.id} & '+V[self.stiffeners[0].type]+' & '  + out_stif
            out_stif += '\\tabularnewline \\hline\n'
            return out_plate, out_stif 
        else:
            return out_plate, ''  

    def __repr__(self) -> str:
        tmp = repr(self.stiffeners[0]) if len(self.stiffeners) != 0 else "No Stiffeners"
        return f"stiff_plate({self.id},{self.plate},{self.spacing},{tmp})"

    def CenterOfArea(self):
        total_A = self.plate.area 
        total_A_n50 = self.plate.n50_area 
        total_Mx = self.plate.area*self.plate.CoA[1]
        total_My = self.plate.area*self.plate.CoA[0]
        if len(self.stiffeners) != 0:
            for i in self.stiffeners:
                total_A += i.area
                total_A_n50 += i.n50_area
                total_Mx += i.area*i.CoA[1]
                total_My += i.area*i.CoA[0]
        
        self.CoA  = (total_Mx/total_A,total_My/total_A) 
        self.area = total_A
        self.n50_area = total_A_n50
    
    def calc_I (self,n50):
        if n50:
            Ixx = self.plate.calc_I_global(self.plate.n50_Ixx_c,self.plate.n50_Iyy_c,
                                            {'axis': 'x','offset': self.CoA[1]})
            Iyy = self.plate.calc_I_global(self.plate.n50_Ixx_c,self.plate.n50_Iyy_c,
                                            {'axis': 'y','offset': self.CoA[0]})
            if len(self.stiffeners) != 0:
                for i in self.stiffeners:
                    Ixx += i.calc_I_global(i.n50_Ixx_c,i.n50_Iyy_c,
                                            {'axis': 'x','offset': self.CoA[1]})
                    Iyy += i.calc_I_global(i.n50_Ixx_c,i.n50_Iyy_c,
                                            {'axis': 'y','offset': self.CoA[0]})
        else:
            Ixx = self.plate.calc_I_global(self.plate.Ixx_c,self.plate.Iyy_c,
                                            {'axis': 'x','offset': self.CoA[1]})
            Iyy = self.plate.calc_I_global(self.plate.Ixx_c,self.plate.Iyy_c,
                                            {'axis': 'y','offset': self.CoA[0]})
            if len(self.stiffeners) != 0:
                for i in self.stiffeners:
                    Ixx += i.calc_I_global(i.Ixx_c,i.Iyy_c,
                                            {'axis': 'x','offset': self.CoA[1]})
                    Iyy += i.calc_I_global(i.Ixx_c,i.Iyy_c,
                                            {'axis': 'y','offset': self.CoA[0]})
        return Ixx, Iyy
    def render(self,r_m='w_b'):
        plt.axis('square')
        self.plate.render(r_m=r_m)
        [i.render() for i in self.stiffeners]
    def local_P(self,key,point):
        ''' point can be whatever. As i have no brain capacity to code a check, PLZ use only the roots of the stiffeners '''
        try:
            min_r = 1e5
            index = 0
            for i,data in enumerate(self.Pressure[key]):
                radius = math.sqrt((data[0]-point[0])**2+(data[1]-point[1])**2)
                if min_r > radius:
                    index = i
                    min_r = radius
            # c_info(f'self.Pressure : {self.Pressure[key][index]}')
            return self.Pressure[key][index][-1]
                
        except KeyError:
            c_error(f'(classes.py) stiff_plate/local_P: The {key} condition has not been calculated for this plate.')
            quit()
    def update(self):
        self.plate.update()
        for stiff in self.stiffeners:
            stiff.update()
        self.CenterOfArea()
        self.Ixx, self.Iyy = self.calc_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.calc_I(n50=True)

class block():
    """
    ------------------------------------------\n
    Block class can be useful to evaluate the plates that consist a part of the Midship 
    Section, ie. a Water Ballast tank, or Cargo Space.\n
    This is done to further enhance the clarity of what substances are in contact with certain plates.\n
    Currently are supported 5 Volume Categories :\n
    1) Water Ballast -> type : WB\n
    2) Dry Cargo -> type: DC\n
    3) Liquid Cargo -> type: LC    \n
    4) Fuel Oil/ Lube Oil/ Diesel Oil -> type: OIL\n
    5) Fresh Water -> type: FW\n
    6) Dry/Void Space -> type: VOID\n
    ------------------------------------------\n
    In order to properly calculate the Pressure Distributions the normal Vectors need to be properly evaluated. Is considered that the Global Positive
    Direction is upwards of Keel (z = 0) towards the Main Deck. However, the local positive axis are outwards for the internal Tanks and inwards for
    the SEA and ATMosphere Blocks. So, pay attention to the way the plates are inserted and blocks are evaluated.
    \nIt would be preferable to have a counterclockwise plate definition order for shell plates and a clockwise order for internal plates. Also, use
    the minus before each plate id at the input file to address the block's boundary direction on the specified plate.\n
    For example,
    a shell plate at Draught has a certain orientation that is uniform with the SEA block (the stiffeners (and normals) are facing inwards) while the WB
    block requires a different direction (normals facing outwards). For this purpose, the id in the WB block would be -id.
    \n!!! BE CAREFUL THAT A CLOSED SMOOTH GEOMETRY IS CREATED !!!\n Verify the block appropriate set up using the *block_plot(ship)* and
    *pressure_plot(ship,'Null','<block tag>')* rendering methods.
    """

    def __init__(self,name:str,symmetrical:bool,space_type:str, list_plates_id : list[int],*args):
        TAGS = ['WB','DC','LC','OIL','FW','VOID']
        """
        We need to pass the type of Cargo that is stored in the Volume and out of which stiffened plates it consists of
        """
        self.name = name
        self.symmetrical = symmetrical # Symmetry around the Z-axis
        if space_type in TAGS:
            self.space_type = space_type
        else:
            c_error("The block type is not currently supported or non-existent.")
        self.list_plates_id = list_plates_id

        # containing the various coefficients to calculate internal pressures
        # for the time being static initialization through space type var
        self.payload = {} 

        self.coords = []
        self.pressure_coords = []
        self.plates_indices = [] # Holds data for the plate's id at a certain grid point
        self.CG = []

        self.eta = [] # Evaluates the normal vectors of each block
        self.Pressure = {} #Pass each Load Case index as key and values as a list
        if self.space_type == 'DC':
            self.Kc = []
        else: self.Kc = None

    
    def __repr__(self):
        return f"BLOCK: type:{self.space_type}, ids: {self.list_plates_id}"
    def __str__(self):
        return f"BLOCK : {self.name} of type {self.space_type}"
    def Kc_eval(self,start,end,stiff_plate_type):
        if self.Kc != None:
            try:
                kc = lambda a : math.cos(a)**2+(1-math.sin(d2r(self.payload['psi'])))*math.sin(a)**2
            except KeyError:
                c_error(f'(classes.py) Class block/Kc_eval : The required \'psi\' value is missing in the payload declaration.')
                quit()
            if stiff_plate_type not in (3,5,4):
                dx = end[0]-start[0]
                dy = end[1]-start[1]
                alpha = math.atan2(dy,dx)
                self.Kc.append(kc(alpha))
            else: self.Kc.append(0)
        else:pass


    def get_coords(self,stiff_plates:list[stiff_plate]):
        '''
        Get the coordinates of the block from its list of plates. TO BE CALLED AFTER THE BLOCKS ARE VALIDATED!!!
        If the block is not calculated correctly then you need to change the id order in the save file.
        '''
        # for i in self.list_plates_id:
        Dx = 0.1
        Mx,My = (0,0)
        A = 0 
        start_p = []
        c = 0
        while c < len(self.list_plates_id):
            for j in stiff_plates:
                if j.id == abs(self.list_plates_id[c]):
                    if self.list_plates_id[c] >= 0:
                        start = j.plate.start
                        end   = j.plate.end
                    elif self.list_plates_id[c] <0:
                        start = j.plate.end
                        end   = j.plate.start
                    if len(self.coords)!= 0:
                        c += 1
                        N = j.plate.length//Dx # Weight the points relative to plate length
                        if start not in self.coords:
                            self.coords.append(start)
                            self.Kc_eval(start,end,j.tag)
                            self.plates_indices.append(j.id)
                            Mx += N*start[0]-start_p[0]
                            My += N*start[1]-start_p[1]
                            A  += N*1
                        if end not in self.coords:
                            if j.tag == 4: #Bilge
                                X,Y = j.plate.render_data()[:2]
                                s = len(X)-2
                                for i in range(1,len(X)-1):
                                    self.coords.append((X[i],Y[i]))
                                    self.Kc_eval(start,end,j.tag)
                                    self.plates_indices.append(j.id)
                                    Mx += N*X[i]/s-start_p[0]
                                    My += N*Y[i]/s-start_p[1]
                                    A  += N*1/s
                            else:
                                self.coords.append(end)
                                self.Kc_eval(start,end,j.tag)
                                self.plates_indices.append(j.id)
                                Mx += N*end[0]-start_p[0]
                                My += N*end[1]-start_p[1]
                                A  += N*1
                    elif len(self.coords) == 0:
                        # c is not incremented to re-parse the first plate and register its end point
                        self.coords.append(start)
                        self.Kc_eval(start,end,j.tag)
                        self.plates_indices.append(j.id)
                        start_p = start
                        A    += j.plate.length//Dx
                    
                    break

        self.CG = [Mx/A,My/A] if not self.symmetrical else [0,My/A]
        self.calculate_pressure_grid(10)
        # self.calculate_CG()

    def calculate_pressure_grid(self,resolution:int):
        '''
        Create a 1D computational mesh to calculate the loads pressure distributions.
        Simply calculating with the geometric coordinates does not hold enough precision.
        The pressure coordinates are calculated on a standard Ds between two points using linear interpolation.
        '''
        K = []
        P = []
        eta = []
        for i in range(len(self.coords)-1):
            if (self.coords[i] not in self.pressure_coords): #eliminate duplicate entries -> no problems with normal vectors
                self.pressure_coords.append(self.coords[i])
                P.append(self.plates_indices[i])
                if self.Kc != None: K.append(self.Kc[i]) 
            temp = linespace(1,resolution,1)
            dy = self.coords[i+1][1]-self.coords[i][1]
            dx = self.coords[i+1][0]-self.coords[i][0]
            span = math.sqrt(dy**2+dx**2)
            phi = math.atan2(dy,dx)
            for j in temp:
                self.pressure_coords.append((self.coords[i][0]+span/resolution*j*math.cos(phi),self.coords[i][1]+span/resolution*j*math.sin(phi)))
                P.append(self.plates_indices[i])
                if self.Kc != None: K.append(self.Kc[i])
            self.pressure_coords.append(self.coords[i+1])
            P.append(self.plates_indices[i])
            if self.Kc != None: K.append(self.Kc[i+1])

        self.plates_indices = P
        if self.Kc != None: self.Kc = K
        
        self.eta=normals2D(self.pressure_coords)


    def render_data(self):
        X = [i[0] for i in self.coords]
        Y = [i[1] for i in self.coords]
        # P = self.Pressure
        X.append(X[0])
        Y.append(Y[0])
        return X, Y , self.space_type , self.CG[1:]
    
    def pressure_data(self,pressure_index,graphical = False):
        '''
        Returns the Pressure Data for plotting or file output. Note that graphical will force ONES over the actual Data.
        '''
        # TO BE USED  WITH A TRY-EXCEPT STATEMENT ( fixed )
        X = [i[0] for i in self.pressure_coords]
        Y = [i[1] for i in self.pressure_coords]
        try:
            P = self.Pressure[pressure_index] if not graphical else [1 for i in self.plates_indices]
        except KeyError:
            c_warn(f'(classes.py) block/pressure_data: A pressure distribution for block :{self} is not calculated for Dynamic Condition {pressure_index} !!! Treat this appropriately !')
            P = None
        return X,Y,P
    def pressure_over_plate(self,stiff_plate:stiff_plate,pressure_index):
        start = True
        x0,x1 = 0,0
        if (stiff_plate.id in self.list_plates_id) or (-stiff_plate.id in self.list_plates_id):
            for i,val in enumerate(self.plates_indices):
                if val == stiff_plate.id and start:
                    x0 = i
                    start = False
                elif (val != stiff_plate.id or i==len(self.plates_indices)-1) and not start:
                    x1 = i
                    break
            try:
                return [(*self.pressure_coords[i],*self.eta[i],self.Pressure[pressure_index][i]) for i in range(x0,x1+1,1)]
            except KeyError:
                if self.space_type != 'ATM' and pressure_index != 'STATIC': #known and expected scenario, thus no need for warning spam
                    c_warn(f'(classes.py) block/pressure_over_plate: {pressure_index} is not calculated for block {self}.\n !Returning zeros as pressure!')
                return [(*self.pressure_coords[i],*self.eta[i],0) for i in range(x0,x1+1,1)]
        else:
            print('blyat',stiff_plate,'cyka',self)
            return None




class Sea_Sur(block):
    def __init__(self,list_plates_id: list[int]):
        super().__init__("SEA",True,'VOID',list_plates_id)
        self.space_type = "SEA"

    def get_coords(self, stiff_plates:list[stiff_plate]):
        super().get_coords(stiff_plates)
        #add a buffer zone for sea of 2 m
        if len(self.coords) == 0:
            c_error("SEA Boundary plates are missing!. The program terminates...")
            quit()
        end = self.coords[-1]
        self.coords.append((end[0]+2,end[1]))
        self.coords.append((end[0]+2,self.coords[0][1]-2))
        self.coords.append((self.coords[0][0],self.coords[0][1]-2))
class Atm_Sur(block):
    def __init__(self,list_plates_id: list[int]):
        super().__init__("ATM",True,'VOID',list_plates_id)
        self.space_type = "ATM"

    def get_coords(self, stiff_plates:list[stiff_plate]):
        super().get_coords(stiff_plates)
        #add a buffer zone for atmosphere of 2 m
        if len(self.coords) == 0:
            c_error("WEATHER DECK Boundary plates are missing!. The program terminates...")
            quit()
        end = self.coords[-1]
        self.coords.append((end[0],end[1]+2))
        self.coords.append((self.coords[0][0]+2,self.coords[0][1]+2))
        self.coords.append((self.coords[0][0]+2,self.coords[0][1]))


class ship():

    def __init__(self, LBP,Lsc, B, T, Tmin, Tsc, D, Cb, Cp, Cm, DWT,PSM_spacing, 
                    stiff_plates:list[stiff_plate],blocks:list[block]):
        self.symmetrical = True # Checks that implies symmetry. For the time being is arbitary constant
        self.LBP = LBP
        self.Lsc = Lsc   # Rule Length
        self.B  = B
        self.T  = T
        self.Tmin = Tmin # Minimum Draught at Ballast condition
        self.Tsc = Tsc   # Scantling Draught
        self.D = D
        self.Cb = Cb
        self.Cp = Cp
        self.Cm = Cm
        self.DWT = DWT
        self.PSM_spacing = PSM_spacing
        self.Mwh = 0
        self.Mws = 0
        self.Msw_h_mid = 0
        self.Msw_s_mid = 0
        self.Cw = 0
        self.Cw_calc()
        self.Moments_wave()
        self.Moments_still()
        #Array to hold all of the stiffened plates
        self.stiff_plates = stiff_plates
        self.blocks = self.validate_blocks(blocks)
        self.evaluate_sea_n_air()
        [(i.get_coords(self.stiff_plates),i.CG.insert(0,self.Lsc/2)) for i in self.blocks]# bit of a cringe solution that saves time
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.Calculate_I(n50=True)

        self.a0 = (1.58-0.47*self.Cb)*(2.4/math.sqrt(self.Lsc)+34/self.Lsc-600/self.Lsc**2) # Acceleration parameter Part 1 Chapter 4 Section 3 pp.180
    def evaluate_beff(self):
        '''
        To be used after corrosion addition evaluation. Plates have -1 mm initial corrosion.
        '''
        [plate.b_eff(self.PSM_spacing) for plate in self.stiff_plates] # b effective evaluation 
    def validate_blocks(self,blocks :list[block]):
        # The blocks are already constructed but we need to validate their responding plates' existence
        ids = [i.id for i in self.stiff_plates]
        for i in blocks:
            for j in i.list_plates_id:
                if (abs(j) not in ids):
                    c_error(f"ship.validate_blocks: The block: {repr(i)} has as boundaries non-existent plates.Program Terminates")
                    quit()
            self.block_properties(i)
        return blocks
    
    def evaluate_sea_n_air(self):
        def atm_key(item: stiff_plate):
            return item.plate.start[0]
        shell_ = []
        deck_ = []
        for i in self.stiff_plates:
            if i.tag == 0 or i.tag == 4:
                shell_.append(i.id)
            elif i.tag == 5:
                deck_.append(i.id)
        self.blocks.append(Sea_Sur(shell_))
        self.blocks.append(Atm_Sur(deck_))

    def block_properties(self,block:block):
        '''
        Function built to give each block its contents properties\n
        For the time being the contents are static and case specific!\n
        In the Future maybe a more dynamic approach will be implemented.
        '''
        # print(block.CG) # bit of a cringe solution that saves time
        # block.CG.insert()
        # print(block.CG) 
        
        if block.space_type in LOADS:
            block.payload = LOADS[block.space_type]
        elif block.space_type in ["SEA","ATM"]:
            pass
        else:
            c_warn('(classes.py) ship/block_properties: The Current block space type does not correspond to a specified load.\n Check your input. Defaulting to type of VOID cargo for block :'+str(block))

    def Cw_calc(self):
        #CSR PART 1 CHAPTER 4.2
        if self.Lsc <= 300 and self.Lsc >= 90: 
            self.Cw = 10.75-((300-self.Lsc)/100)**1.5
        elif self.Lsc <= 350 and self.Lsc >= 300: 
            self.Cw = 10.75
        elif self.Lsc <= 500 and self.Lsc >= 350: 
            self.Cw = 10.75-((self.Lsc-350)/150)**1.5
        else:
            c_error("ship.Cw_Calc: The Ship's LBP is less than 90 m or greater than 500 m. The CSR rules do not apply.")
            quit()

    def Moments_wave(self):
        # CSR PART 1 CHAPTER 4.3
        #
        # fm = {
        #     "<= 0" : 0.0,
        #     0.4 : 1.0,
        #     0.65: 1.0,
        #     ">= Lbp": 0.0
        # }

        self.Mws = -110*self.Cw*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        self.Mwh =  190*self.Cw*self.LBP**2*self.B*self.Cb*1e-3

    def Moments_still(self):
        # CSR PART 1 CHAPTER 4.2
        # self.Msw_h_mid = (171*((self.Cb+0.7)-190*self.Cb))*self.Cw*self.LBP**2*self.B*1e-3
        # self.Msw_s_mid =  -51.85*self.Cw*self.LBP**2*self.B*(self.Cb+0.7)*1e-3
        # CSR page 187
        # fsw = {
        #     "<= 0 " : 0.0,
        #     0.1  : 0.15,
        #     0.3 : 1.0,
        #     0.7 : 1.0,
        #     0.9 : 0.15,
        #     ">= Lbp" : 0
        # }
        self.Msw_h_mid = 171*(self.Cb+0.7)*self.Cw*self.LBP**2*self.B*1e-3 - self.Mwh
        self.Msw_s_mid = -0.85*(171*(self.Cb+0.7)*self.Cw*self.LBP**2*self.B*1e-3 + self.Mws)

    def calc_CoA(self):
        area  = 0 
        MoM_x = 0 
        MoM_y = 0

        for i in self.stiff_plates:
            area += i.area
            MoM_x += i.area*i.CoA[1]
            MoM_y += i.area*i.CoA[0]

        return MoM_x/area, MoM_y/area, area

    def Calculate_I(self,n50):
        Ixx = 0
        Iyy = 0
        for i in self.stiff_plates:
            if n50:
                Ixx += i.n50_Ixx_c + (i.CoA[1]-self.yo)**2*i.area
                Iyy += i.n50_Iyy_c + (i.CoA[0]-self.xo)**2*i.area
            else:
                Ixx += i.Ixx_c + (i.CoA[1]-self.yo)**2*i.area
                Iyy += i.Iyy_c + (i.CoA[0]-self.xo)**2*i.area
        if self.symmetrical: return 2*Ixx, 2*Iyy
        else: return Ixx, Iyy 

    def render(self,r_m='w'):
        fig = plt.figure()
        for i in self.stiff_plates:
            i.render(r_m=r_m)
        # plt.axis([-1,self.B/2+1,-1,self.D+3])
        plt.show()
    def update(self,update_all=False):
        if update_all:
            [i.update() for i in self.stiff_plates]
        self.yo, self.xo, self.cross_section_area = self.calc_CoA()
        self.Ixx, self.Iyy = self.Calculate_I(n50=False)
        self.n50_Ixx, self.n50_Iyy = self.Calculate_I(n50=True)
    def Debug(self):
        print('symmetrical : ',self.symmetrical)
        print('LBP : ',self.LBP)
        print('Lsc : ',self.Lsc)
        print('B : ',self.B)
        print('T : ',self.T)
        print('Tmin : ',self.Tmin)
        print('Tsc : ',self.Tsc)
        print('D : ',self.D)
        print('Cb : ',self.Cb)
        print('Cp : ',self.Cp)
        print('Cm : ',self.Cm)
        print('DWT : ',self.DWT)
        print('PSM_spacing : ',self.PSM_spacing)
        print('Mwh : ',self.Mwh)
        print('Mws : ',self.Mws)
        print('Msw_h_mid : ',self.Msw_h_mid)
        print('Msw_s_mid : ',self.Msw_s_mid)
        print('Cw : ',self.Cw)
        print('STIFF PLATES')
        [print(i) for i in self.stiff_plates]
        print('BLOCKS')
        [print(i,2) for i in self.blocks]
        print('yo : ', self.yo)
        print('Ixx : ', self.Ixx)
        print('n50_Ixx : ', self.n50_Ixx)
        print('a0 : ', self.a0)

    def Data_Input(self, text):
        # Do stuff with text
        self.data += text

    def LaTeX_output(self,Debug=False,standalone=False,figs = ()):
        '''
        Output Function that generates a .tex file for use in LaTeX
        
        '''
        mid = ''
        GeneralPart = (
            '\\chapter{General Particulars}\n'
            '\\label{sec:General Particulars}\n'
            '\\begin{table}[h]\n'
            '\\caption{Ship\'s General Particulars}\n'
            '\\label{tab:Gen_Part}\n'
            '\\begin{tabular}{{>{\centering}m{6cm}}*{2}{>{\centering}m{4cm}}}\n'
            '\\hline\n'
            '$L_{BP}$ '+f'&{self.LBP}&'+' [m]\\tabularnewline \\hline\n'
            '$L_{sc} = L$ '+f'&{self.Lsc}&'+' [m]\\tabularnewline \\hline\n'
            '$B$ '+f'&{self.B}&'+' [m]\\tabularnewline \\hline\n'
            '$T$ '+f'&{self.T}&'+' [m]\\tabularnewline \\hline\n'
            '$T_{min}$ '+f'&{self.Tmin}&'+' [m]\\tabularnewline \\hline\n'
            '$T_{sc}$ '+f'&{self.Tsc}&'+' [m]\\tabularnewline \\hline\n'
            '$D$ '+f'&{self.D}&'+' [m]\\tabularnewline \\hline\n'
            '$C_b$ '+f'&{self.Cb}&'+' \\tabularnewline \\hline\n'
            '$C_p$ '+f'&{self.Cp}&'+' \\tabularnewline \\hline\n'
            '$C_m$ '+f'&{self.Cm}&'+' \\tabularnewline \\hline\n'
            '$DWT$ '+f'&{self.DWT}&'+' \\tabularnewline \\hline\n'
            'PSM spacing '+f'&{self.PSM_spacing}&'+' [m]\\tabularnewline \\hline\n'
            '$M_{wh}$ '+f'&{round(self.Mwh,2)}&'+' [kNm]\\tabularnewline \\hline\n'
            '$M_{ws}$ '+f'&{round(self.Mws,2)}&'+' [kNm]\\tabularnewline \\hline\n'
            '$M_{sw,h-mid}$ '+f'&{round(self.Msw_h_mid,2)}&'+' [kNm]\\tabularnewline \\hline\n'
            '$M_{sw,s-mid}$ '+f'&{round(self.Msw_s_mid,2)}&'+' [kNm]\\tabularnewline \\hline\n'
            '$C_w$ '+f'&{round(self.Cw,3)}&'+' \\tabularnewline \\hline\n'
            '$y_{neutral}$ '+f'&{round(self.yo,3)}&'+' [m]\\tabularnewline \\hline\n'
            '$I_{net,\, v}$ '+f'&{round(self.Ixx,2)}&'+' [$m^4$]\\tabularnewline \\hline\n'
            '$I_{n-50,\, v}$ '+f'&{round(self.n50_Ixx,2)}&'+' [$m^4$]\\tabularnewline \\hline\n'
            '$a_0$   '+f'&{round(self.a0,5)}&'+' \\tabularnewline \\hline\n'
            '\\end{tabular}\n'
            '\\end{table}\n\n')
        figures = ''
        if len(figs) != 0:
            for i in figs:
                figures+=(
                    '\\begin{figure}[h]\n'
                    '\\centering\n'
                    '\\includegraphics[width=\linewidth]{'
                    f'{i}'
                    '}\n\\end{figure}\n')

        plates = (
            '\\chapter{Plating Data}\n'
            '\\label{sec:Plating Data}\n'
            '\\begin{table}[h]\n'
            '\\caption{Ship\'s Plating Data}\n'
            '\\label{tab:Plates_Data}\n'
            '\\begin{adjustbox}{center}\n'
            '\\begin{tabular}{*{8}{>{\centering}m{2cm}}}\n'
            '\\hline\n'
            'No & Material & Breadth & Spacing & Center of Area & Thickness & Net Thickness & Corrosion Thickness \\tabularnewline \\hline\n'
            '   &          &    [m]   & [mm]   & $(y,z)$ [m]    &    [mm]   &    [mm]   &    [mm]   \\tabularnewline \\hline\n')
        stiffeners = (
            '\\chapter{Stiffeners Data}\n'
            '\\label{sec:Stiffeners Data}\n'
            '\\begin{table}[h]\n'
            '\\caption{Ship\'s Stiffeners Data}\n'
            '\\label{tab:Stiff_Data}\n'
            '\\begin{adjustbox}{center}\n'
            '\\begin{tabular}{*{8}{>{\centering}m{2cm}}}\n'
            '\\hline\n'
            'No & Type & & Material & L   & Thickness & Net Thickness & Corrosion Thickness \\tabularnewline \\hline\n'
            '   &      & &          & [mm] & [mm]      &    [mm]       &    [mm]            \\tabularnewline \\hline\n') 
        for i in self.stiff_plates:
            tmp = i.LaTeX_output()
            plates += tmp[0]
            stiffeners += tmp[1]
        
        plates += '\\end{tabular}\n\\end{adjustbox}\n\\end{table}\n\n'
        stiffeners += '\\end{tabular}\n\\end{adjustbox}\n\\end{table}\n\n'
        mid += GeneralPart+figures+plates+stiffeners 
        
        if standalone:
                    out = ('\\documentclass[12pt,a4paper]{report}\n\\usepackage{array}\n'
                '\\usepackage{multirow}\n'
                '\\usepackage{adjustbox}\n'
                '\\usepackage{spalign}\n'
                '\\usepackage{amsmath}\n'
                '\\usepackage{comment}\n'
                '\\usepackage{caption}\n'
                '\\begin{document}\n'+mid+''
                '\\end{document}')
        else:
            out = mid

        if Debug: print(out)
        return out
        
#end of file