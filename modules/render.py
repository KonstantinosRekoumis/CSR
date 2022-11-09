from cgitb import enable
import math
import ezdxf
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import modules.classes as cls
import numpy as np
from modules.utilities import c_error,c_warn,c_success,c_info

def normalize(a:list):
    max = -1
    for i in a:
        if (abs(i)>max) and (abs(i)!=0):
            max = abs(i)
    
    return [x/max for x in a]


def normals2D(geom,flip_n = False,show_norms = False):
    eta = np.ndarray((len(geom)-1,2))
    for i in range(len(geom)-1):
        xba = geom[i+1,0]-geom[i,0]
        yba = geom[i+1,1]-geom[i,1]
        if flip_n:
            yba = - yba
            xba = - xba
        nrm2 = np.sqrt(yba**2+xba**2)
        if nrm2 == 0:
            eta[i,0] = yba/nrm2
            eta[i,1] = -xba/nrm2
            c_warn(f"eta = {eta}, norm = {nrm2}, geom = {geom}")
        else:
            eta[i,0] = yba/nrm2
            eta[i,1] = -xba/nrm2
    # last point
    # eta[-1,:] = eta[-2,:]


    if show_norms:# Debug only for standalone call
        fig, ax = plt.subplots()
        ax.plot(geom[0:-2,0],geom[0:-2,1])
        ax.quiver(geom[0:-2,0],geom[0:-2,1],eta[:,0],eta[:,1])
        plt.show()
    
    return eta

def lines_plot(ship:cls.ship,show_w=False,color = "black",
                axis_padding = (3,1),show=True):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item,
    show_w : Boolean, If True -> the plates seams are shown
    color : String, describes the color to plot the lines
    """
    if show_w :
        marker = '*'
    else:marker = ""

    fig,ax = plt.subplots(1,1)
    for i in ship.stiff_plates:
        X,Y = i.plate.render_data()[:2]
        ax.plot(X,Y,marker=marker,color = color)
        for j in i.stiffeners:
            ax.plot(*j.render_data()[:2],color = color)
    ax.set_ylim([-1,ship.D+axis_padding[0]])
    ax.set_xlim([-1,ship.B/2+axis_padding[1]])
    # ax.set_aspect()
    if show:plt.show()
    return fig,ax

def block_plot(ship:cls.ship,show_w = True,color = 'black',fill = True):
    if show_w :
        marker = '*'
    else:marker = ""

    colors = {
        'SEA':'blue',
        'ATM':'lightcyan',
        'WB':'turquoise',
        'DC':'tomato',
        'OIL':'darkgoldenrod',
        'FW':'aqua',
        'VOID':'silver'
    }

    fig,ax = plt.subplots(1,1)
    for i in ship.blocks:
        X,Y,TAG,pos = i.render_data()
        # if TAG in ('SEA','ATM'): continue
        # pos = (X[(len(X)//2)],Y[(len(Y)//2)])
        ax.fill(X,Y,color = colors[i.space_type]) if fill else ax.plot(X,Y,color = colors[i.space_type],marker = marker)
        ax.annotate(TAG,pos,color=colors[i.space_type])

    ax.set_ylim([-3,ship.D+3])
    ax.set_xlim([-3,ship.B/2+3])
    # ax.set_aspect()
    plt.show()

def contour_plot(ship:cls.ship,show_w=False,cmap='Set2',color = 'black',key = 'thickness',path=''):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item,
    show_w : Boolean, If True -> the plates seams are shown
    """
    if show_w :
        marker = "."
    else:marker = ""

    X = []
    Y = []
    T = []
    M = []
    Tag = []
    Id = []
    fig,ax = plt.subplots(1,1)
    for i in ship.stiff_plates:
        if i.null and key != 'tag': continue # skip rendering null plates except for locality
        x,y,t,m,tag = i.plate.render_data()
        X.append(x)
        Y.append(y)
        T.append(t*1e3)
        M.append(m)
        Tag.append(tag)
        Id.append(i.id)

        for j in i.stiffeners:
            ax.plot(*j.render_data()[:2],color = color)
    data = {
        'thickness':[T,'number'],
        'material':[M,'string'],
        'tag':[Tag,'string'],
        'id':[Id,'number']
    }

    ax.set_ylim([-1,ship.D+3])
    ax.set_xlim([-1,ship.B/2+1])
    try:
        fig,ax = c_contour(X,Y,data[key][0],key,fig,ax,cmap,key = data[key][1])
        plt.title(f'Plating\'s {key} Plot')
        ax.invert_xaxis()
        if path !='':
            plt.savefig(path,bbox_inches='tight',orientation = "landscape")
        else:
            plt.show()
    except KeyError:
        c_warn(f'(render.py) contour_plot(): Key :{key} is not valid. Valid options are \'thickness\',\'material\',\'tag\',\'id\'. Thus no plot is produced.')
        pass


def pressure_plot(ship:cls.ship, pressure_index :str, block_types: str, normals_mode = False,quiver=False):
    """
    Rendering Function using the Matplotlib library. Is used to graph the pressure distribution on each plate's face.
    This is done by calculating each plate's normal vector and applying the pressure on it to get a graph.\n
    ----------------- BE CAREFUL THAT A PRESSURE CASE HAS BEEN CALCULATED BEFORE PLOTTING -----------------
    Input args:\n
    ship-> A ship class item\n
    pressure_index -> The pressure distribution case key (For example: 'HSM-1' -> HSM - 1 case).\n
    args -> optional arguments passed to the base lines_plot func call
    """
    # Use the pressure distribution saved in each block
    fig,ax = lines_plot(ship,show_w=True,show=False,axis_padding=(10,10))
    Plot_X = []
    Plot_Y = []
    Data = []
    for i in ship.blocks:
        _Px_ = []
        _Py_ = []
        if block_types == 'all': enabled = True
        elif i.space_type in block_types: enabled = True
        else: enabled = False
        
        if not enabled: continue
        
        X,Y,P = i.pressure_data(pressure_index,graphical=normals_mode)

        if P != None:
            # print(f'Block: {i.name} P : ',P)
            Data = [*Data,math.nan,math.nan,*P,math.nan,math.nan]
            P = normalize(P)
        else:
            continue
        
        for j,x in enumerate(X):
            if j == 0:
                eta = normals2D(np.array([[X[0],Y[0]],[X[1],Y[1]]]),flip_n=True,show_norms=False) 

                _Px_.append(eta[0,0]*P[j])
                _Py_.append(eta[0,1]*P[j])
            else:
                eta = normals2D(np.array([[X[j],Y[j]],[X[j-1],Y[j-1]]]),flip_n=False,show_norms=False) 
                _Px_.append(eta[0,0]*P[j])
                _Py_.append(eta[0,1]*P[j])

        Plot_X = [*Plot_X,math.nan,X[0],*[X[i]+_Px_[i]*2 for i in range(len(X))],X[-1]]
        Plot_Y = [*Plot_Y,math.nan,Y[0],*[Y[i]+_Py_[i]*2 for i in range(len(X))],Y[-1]]

        # ax.plot(Plot_X,Plot_Y)
    fig,ax=c_contour(Plot_X,Plot_Y,Data,"Pressure [kPa]",fig,ax,'jet',marker='.')
    ax.plot((-3,ship.B/2+3),(ship.T,ship.T))
    ax.set_ylim([-3,ship.D+3])
    ax.set_xlim([-3,ship.B/2+3])
    plt.title(f"Pressure Distribution for {pressure_index}")
    plt.show()

    return fig,ax

def c_contour(X,Y,data,data_label,fig,ax,cmap,key="number",marker="+",lines = True):
    _map_ = ScalarMappable(cmap=cmap)
    if key == "number":
        vals = []
        for i in data:
            if type(i)==str: 
                c_error("(render.py) c_contour: Detected item of type <str>. Considering changing the key value to string.")
                quit()
            if (i not in vals) and (i != math.nan):
                vals.append(i) 
        vals.sort()
        _map_.set_array(vals)
        cb = fig.colorbar(_map_,cmap=cmap)
        cb.ax.set_title(data_label)
    elif key == "string":
        vals = []
        text = []
        d_map = {}
        c = 1
        for i in data:
            if i not in d_map:
                d_map[i] = c
                d_map[c] = i
                vals.append(c)
                text.append(i)
                c += 1
        
        vals.sort()
        _map_.set_array(vals)
        cb = fig.colorbar(_map_,ticks=vals)
        cb.ax.set_title(data_label)
        cb.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(text):
            cb.ax.text(4,  j+1 , lab, ha='center', va='center')

    for i in range(len(X)):
        breaks = 0 #Int to increment where a break by nan is encountered
        if key == "string":
            val = d_map[data[i-breaks]]
        elif key == "number":
            val = data[i-breaks]
        
        if type(X[i]) in (list,tuple,np.ndarray):
            ax.plot(X[i],Y[i],color = _map_.to_rgba(val),marker = marker) # passing line coordinates as arguments. NaN is handled internally by plot
        else:
            if (X[i]!= math.nan) and (Y[i] != math.nan):
                ax.plot(X[i],Y[i],color = _map_.to_rgba(val),marker = marker)
                if lines and (i>0): # situational based on the data type
                    ax.plot((X[i],X[i-1]),(Y[i],Y[i-1]),color = _map_.to_rgba(val))
            else:
                ax.plot(X[i],Y[i])
                breaks+=1
    
    return fig,ax









