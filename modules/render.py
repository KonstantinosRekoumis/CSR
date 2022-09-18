import math
import ezdxf
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import classes as cls
import numpy as np
from utilities import c_error,c_warn,c_success,c_info

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


    if show_norms:# Debug only
        fig, ax = plt.subplots()
        ax.plot(geom[0:-2,0],geom[0:-2,1])
        ax.quiver(geom[0:-2,0],geom[0:-2,1],eta[:,0],eta[:,1])
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
        X,Y,P,TAG,pos = i.render_data()
        # pos = (X[(len(X)//2)],Y[(len(Y)//2)])
        ax.fill(X,Y,color = colors[i.space_type]) if fill else ax.plot(X,Y,color = colors[i.space_type],marker = marker)
        plt.annotate(TAG,pos,color=colors[i.space_type])
    ax.set_ylim([-3,ship.D+3])
    ax.set_xlim([-3,ship.B/2+3])
    # ax.set_aspect()
    plt.show()

def contour_plot(ship:cls.ship,show_w=False,color = 'black',key = 'thickness'):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item,
    show_w : Boolean, If True -> the plates seams are shown
    """
    index = {
        'thickness':2,
        'material':3
    }

    if show_w :
        marker = "."
    else:marker = ""

    X = []
    Y = []
    T = []
    M = []
    Tag = []
    fig,ax = plt.subplots(1,1)
    for i in ship.stiff_plates:
        x,y,t,m,tag = i.plate.render_data()
        X.append(x)
        Y.append(y)
        T.append(t*1e3)
        M.append(m)
        Tag.append(tag)

        for j in i.stiffeners:
            plt.plot(*j.render_data()[:2],color = color)

    ax.set_ylim([-1,ship.D+3])
    ax.set_xlim([-1,ship.B/2+1])

    _map_ = ScalarMappable(cmap="Set1")
    if key == "thickness":
        vals = []
        for i in T:
            if i not in vals:
                vals.append(i)        
        vals.sort()
        _map_.set_array(vals)
        fig.colorbar(_map_,)

    elif key == "material" or key == "tag":
        vals = []
        mats = []
        d_map = {}
        c = 1
        if key == "material":
            Data = M
        elif key == "tag":
            Data = Tag

        for i in Data:
            if i not in d_map:
                d_map[i] = c
                d_map[c] = i
                vals.append(c)
                mats.append(i)
                c += 1
        
        vals.sort()
        _map_.set_array(vals)
        cb = fig.colorbar(_map_,ticks=vals)
        cb.ax.get_yaxis().set_ticks([])

        for j, lab in enumerate(mats):
            cb.ax.text(2,  j+1 , lab, ha='center', va='center')

    for i in range(len(X)):
        if key == "material":
            val = d_map[M[i]]
        elif key == "tag":
            val = d_map[Tag[i]]
            if Tag[i] == "Bilge": 
                marker =""
            else:
                marker = '.'
        elif key == "thickness":
            val = T[i]
        plt.plot(X[i],Y[i],color = _map_.to_rgba(val),marker = marker)

    plt.show()

def pressure_plot(ship:cls.ship, pressure_index :str, *args):
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
        try:
            X,Y,P = i.pressure_data(pressure_index)
            Data = [*Data,math.nan,math.nan,*P,math.nan,math.nan]
            P = normalize(P)
        except KeyError:
            c_info(f"Pressure at block {i} is not calculated for condition {pressure_index}.")
            continue
        
        for j,x in enumerate(X):
            if j == 0:
                eta = normals2D(np.array([[X[0],Y[0]],[X[1],Y[1]]]),flip_n=True)
                _Px_.append(eta[0,0]*P[j])
                _Py_.append(eta[0,1]*P[j])
            else:
                eta = normals2D(np.array([[X[j],Y[j]],[X[j-1],Y[j-1]]]))
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

def c_contour(X,Y,data,data_label,fig,ax,cmap,key="number",marker="",lines = True):
    _map_ = ScalarMappable(cmap=cmap)
    if key == "number":
        vals = []
        for i in data:
            if type(i)==str: 
                c_error("render/c_contour: Detected item of type <str>. Considering changing the key value to string.")
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
        cb = plt.colorbar(_map_,fig,ticks=vals)
        cb.ax.set_title(data_label)
        cb.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(text):
            cb.ax.text(2,  j+1 , lab, ha='center', va='center')

    for i in range(len(X)):
        breaks = 0 #Int to increment where a break by nan is encountered
        if key == "string":
            val = d_map[data[i-breaks]]
        elif key == "number":
            val = data[i-breaks]

        if (X[i]!= math.nan) and (Y[i] != math.nan):
            ax.plot(X[i],Y[i],color = _map_.to_rgba(val),marker = marker)
            if lines and (i>0): # situational based on the data type
                ax.plot((X[i],X[i-1]),(Y[i],Y[i-1]),color = _map_.to_rgba(val))
        else:
            ax.plot(X[i],Y[i])
            breaks+=1
    
    return fig,ax









