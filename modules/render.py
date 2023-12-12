import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable

from modules.utilities import c_error, c_warn
from modules.baseclass.ship import Ship


def normalize(a: list):
    maxima = max(map(lambda x: abs(x), a))
    maxima = maxima if maxima != 0 else -1

    return list(map(lambda x: x / maxima, a))


def normals_2d(geom, flip_n=False, show_norms=False):
    eta = np.ndarray((len(geom) - 1, 2))
    for i in range(len(geom) - 1):
        xba = geom[i + 1, 0] - geom[i, 0]
        yba = geom[i + 1, 1] - geom[i, 1]
        if flip_n:
            yba = - yba
            xba = - xba
        nrm2 = np.sqrt(yba ** 2 + xba ** 2)
        if nrm2 == 0:
            c_warn(f"eta = {eta}, norm = {nrm2}, geom = {geom}")
            assert nrm2 != 0
        eta[i, 0] = yba / nrm2
        eta[i, 1] = -xba / nrm2

    # Debug only for standalone call
    if show_norms:
        fig, ax = plt.subplots()
        ax.plot(geom[0:-2, 0], geom[0:-2, 1])
        ax.quiver(geom[0:-2, 0], geom[0:-2, 1], eta[:, 0], eta[:, 1])
        plt.show()

    return eta


def lines_plot(ship: Ship, show_w=False, color="black", axis_padding=(3, 1), fig=None, ax=None):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item,
    show_w : Boolean, If True -> the plates seams are shown
    color : String, describes the color to plot the lines
    """
    marker = ""
    if show_w:
        marker = "*"

    # ! gui update passes the fig reference
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1)

    for i in ship.stiff_plates:
        x, y = i.plate.render_data()[:2]
        ax.plot(x, y, marker=marker, color=color)
        for j in i.stiffeners:
            ax.plot(*j.render_data()[:2], color=color)
    ax.set_ylim([-1, ship.D + axis_padding[0]])
    ax.set_xlim([-1, ship.B / 2 + axis_padding[1]])
    return fig, ax


def block_plot(ship: Ship, show_w=True, color="black", fill=True, fig=None, ax=None):
    marker = ""
    if show_w:
        marker = "*"

    colors = {
        "SEA": "blue",
        "ATM": "lightcyan",
        "WB": "turquoise",
        "DC": "tomato",
        "OIL": "darkgoldenrod",
        "FW": "aqua",
        "VOID": "silver"
    }

    # ! gui update passes the fig reference
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1)

    for i in ship.blocks:
        x, y, tag, pos = i.render_data()
        # FIXME this is ugly, must be a better way
        ax.fill(x, y, color=colors[i.space_type]) if fill else ax.plot(x, y, color=colors[i.space_type], marker=marker)
        ax.annotate(tag, pos, color=colors[i.space_type])

    ax.set_ylim([-3, ship.D + 3])
    ax.set_xlim([-3, ship.B / 2 + 3])
    return fig, ax


def contour_plot(ship: Ship, cmap="Set2", color="black", key="thickness", path=None, fig=None, ax=None):
    """
    Rendering Function using the Matplotlib library.
    Input args:
    A ship class item
    """

    x, y, t, m = [], [], [], []
    tag = []
    identifier = []
    psm_spacing = []

    # ! gui update passes the fig reference
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1)

    for i in ship.stiff_plates:
        # skip rendering null plates except for locality
        if i.null and key != "tag":
            continue
        x, y, t, m, tag = i.plate.render_data()
        x.append(x)
        y.append(y)
        t.append(t * 1e3)
        m.append(m)
        tag.append(tag)
        identifier.append(f'{i.id}')
        psm_spacing.append(i.PSM_spacing)

        for j in i.stiffeners:
            ax.plot(*j.render_data()[:2], color=color)

    data = {
        "thickness": [t, "number", "As Built Thickness [mm]"],
        "spacing": [psm_spacing, "string", "Web Section Spacing [m]"],
        "material": [m, "string", "Material"],
        "tag": [tag, "string", "Locality Tag"],
        "id": [identifier, "string", "Plate's Id"]
    }

    ax.set_ylim([-1, ship.D + 3])
    ax.set_xlim([-1, ship.B / 2 + 1])
    try:
        fig, ax = c_contour(x, y, data[key][0], data[key][2], fig, ax, cmap, key=data[key][1])
        plt.title(f"Plating's {key} Plot")
        ax.invert_xaxis()
        if not path:
            plt.savefig(path, bbox_inches='tight', orientation="landscape")
        return fig, ax
    except KeyError:
        c_warn(f"(render.py) contour_plot(): Key :{key} is not valid. "
               f"Valid options are 'thickness', 'material', 'tag', 'id', 'spacing'. Thus no plot is produced.")


def pressure_plot(ship: Ship, pressure_index: str, block_types: str, normals_mode=False, path=None, fig=None, ax=None):
    """
    Rendering Function using the Matplotlib library. Is used to graph the pressure distribution on each plate's face.
    This is done by calculating each plate's normal vector and applying the pressure on it to get a graph.\n
    ----------------- BE CAREFUL THAT A PRESSURE CASE HAS BEEN CALCULATED BEFORE PLOTTING -----------------
    Input args:\n
    ship-> A ship class item\n
    pressure_index -> The pressure distribution case key (For example: 'HSM-1' -> HSM - 1 case).\n
    """
    # Use the pressure distribution saved in each block
    fig, ax = lines_plot(ship, show_w=True, axis_padding=(10, 10), fig=fig, ax=ax)

    plot_x = []
    plot_y = []
    data = []
    for i in ship.blocks:
        _Px_ = []
        _Py_ = []

        enabled = block_types == "all" or i.space_type in block_types
        if not enabled:
            continue

        x, y, p = i.pressure_data(pressure_index, graphical=normals_mode)

        if p is None:
            continue

        data = [*data, math.nan, math.nan, *p, math.nan, math.nan]
        p = normalize(p)

        for j, x in enumerate(x):
            if j == 0:
                eta = normals_2d(np.array([[x[0], y[0]], [x[1], y[1]]]), flip_n=True, show_norms=False)
                _Px_.append(eta[0, 0] * p[j])
                _Py_.append(eta[0, 1] * p[j])
                continue

            eta = normals_2d(np.array([[x[j], y[j]], [x[j - 1], y[j - 1]]]), flip_n=False, show_norms=False)
            _Px_.append(eta[0, 0] * p[j])
            _Py_.append(eta[0, 1] * p[j])

        plot_x = [*plot_x, math.nan, x[0], *[x[i] + _Px_[i] * 2 for i in range(len(x))], x[-1]]
        plot_y = [*plot_y, math.nan, y[0], *[y[i] + _Py_[i] * 2 for i in range(len(x))], y[-1]]

    fig, ax = c_contour(plot_x, plot_y, data, "Pressure [kPa]", fig, ax, "jet", marker=".")
    ax.plot((-3, ship.B / 2 + 3), (ship.T, ship.T))
    ax.set_ylim([-3, ship.D + 3])
    ax.set_xlim([-3, ship.B / 2 + 3])
    ax.invert_xaxis()
    plt.title(f"Pressure Distribution for {pressure_index}")

    if not path:
        plt.savefig(path, bbox_inches="tight", orientation="landscape")

    return fig, ax


def c_contour(x, y, data, data_label, fig, ax, cmap, key="number", marker="+", lines=True):
    d_map = {}
    _map_ = ScalarMappable(cmap=cmap)

    if key == "number":
        vals = []
        for i in data:
            if i is str:
                c_error(
                    "(render.py) c_contour: Detected item of type <str>. Considering changing the key value to string."
                )
                quit()
            if (i not in vals) and (i != math.nan):
                vals.append(i)
        vals.sort()
        _map_.set_array(vals)
        cb = fig.colorbar(_map_, cmap=cmap)
        cb.ax.set_title(data_label)

    if key == "string":
        vals = []
        text = []
        c = 1
        for i in data:
            if i not in d_map:
                d_map[i] = c
                d_map[c] = i
                vals.append(c)
                text.append("- " + str(i))
                c += 1

        vals.sort()
        _map_.set_array(vals)
        cb = fig.colorbar(_map_, ticks=vals)
        cb.ax.set_title(data_label)
        cb.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(text):
            y_off = j + 1 - 0.02
            cb.ax.text(1, y_off, lab, ha="left", va="center")

    for i in range(len(x)):
        breaks = 0  # Int to increment where a break by nan is encountered
        val = data[i - breaks]
        if key == "string":
            val = d_map[data[i - breaks]]

        element_is_list =  isinstance(x[i], list)
        element_is_tuple =  isinstance(x[i], tuple)
        element_is_np_array =  isinstance(x[i], np.ndarray)

        if element_is_list or element_is_tuple or element_is_np_array:
            # passing line coordinates as arguments. NaN is handled internally by plot
            ax.plot(x[i], y[i], color=_map_.to_rgba(val), marker=marker)
            continue

        if x[i] != math.nan and y[i] != math.nan:
            ax.plot(x[i], y[i], color=_map_.to_rgba(val), marker=marker)
            if lines and (i > 0):  # situational based on the data type
                ax.plot((x[i], x[i - 1]), (y[i], y[i - 1]), color=_map_.to_rgba(val))
            continue

        ax.plot(x[i], y[i])
        breaks += 1

    return fig, ax
