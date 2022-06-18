import ezdxf
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import classes as cls
import numpy as np


def lines_plot(ship:cls.ship,show_w=False,color = "black"):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item,
    show_w : Boolean, If True -> the plates seams are shown
    color : String, describes the color to plot the lines
    """
    if show_w :
        marker = 2
    else:marker = ""

    fig,ax = plt.subplots(1,1)
    for i in ship.stiff_plates:
        X,Y = i.plate.render_data()[:2]
        ax.plot(X,Y,marker=marker,color = color)
        for j in i.stiffeners:
            ax.plot(*j.render_data()[:2],color = color)
    ax.set_ylim([-1,ship.D+3])
    ax.set_xlim([-1,ship.B/2+1])
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




