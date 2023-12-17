import math

import numpy as np
from matplotlib import pyplot as plt

from modules.utils.logger import Logger


def set_diff(l1: list, l2: list) -> set:
    """
    Difference between l1 and l2 sets (l2 - l1).
    """

    l1_keys = set(l1)
    l2_keys = set(l2)
    return l2_keys - l1_keys


def d2r(x):
    return x / 180 * math.pi


def normalize(a: list):
    maxima = max(map(lambda x: abs(x), a))
    maxima = maxima if maxima != 0 else -1

    return list(map(lambda x: x / maxima, a))


def linear_inter(start, end, target_x) -> float:
    """
    y_target = (y_end-y_start)/(x_end-x_start)*(target_x-x_start)
    """
    return (end[1] - start[1]) / (end[0] - start[0]) * (target_x - start[0])


def lin_int_dict(vli_dict: dict, key: float, *f_args, suppress=False) -> float:
    """
    Parses a dictionary of values and linear interpolates at key value accordingly
    :argument vli_dict: Dictionary of values and linear interpolates
    """
    # checks whether the function is presented to proper data
    try:
        for i in vli_dict:
            if not (isinstance(i, float) or isinstance(i, int)):
                Logger.warning(i, vli_dict[i])
                raise KeyError
            else:
                if not (isinstance(vli_dict[i], float) or isinstance(vli_dict[i], int)):
                    if callable(vli_dict[i]):
                        if not suppress:
                            Logger.warning("Detected a function. May result in error...")
                            Logger.warning(vli_dict[i])
                    else:
                        Logger.warning(i, vli_dict[i])
                        raise KeyError
    except KeyError:
        Logger.warning(
            "Input dictionary expects both the keys and their values "
            "to be of type float or int.\nThus the program terminates..."
        )
        quit()

    if key in vli_dict:
        out = vli_dict[key]
    else:
        tmp_x = [0, 0]  # first position holds the maximum minimum and the second position the minimum maximum
        tmp_y = [0, 0]  # first position holds the maximum minimum and the second position the minimum maximum
        for i in vli_dict:
            if key > i > tmp_x[0]:
                tmp_x[0] = i
                tmp_y[0] = vli_dict[i] if not callable(i) else i(*f_args)
            elif key < i < tmp_x[0]:
                tmp_x[1] = i
                tmp_y[1] = vli_dict[i] if not callable(i) else i(*f_args)
        out = linear_inter((tmp_x[0], tmp_y[0]), (tmp_x[1], tmp_y[1]), key)
    return out


def linespace(start: int, end: int, step: int, skip=0, truncate_end=True):
    """
    A function that creates a linear space from start to end with step.
    skip = N -> skips every other N element
    """
    out = []
    if not truncate_end: end += 1
    if skip != 0:
        for i, j in enumerate(range(start, end, step)):
            if i % skip != 0 and skip != 0:
                out.append(j)
    else:
        out = [i for i in range(start, end, step)]
    return out


def normals_2d(geom: list, flip_n=False):
    eta = []
    for i in range(len(geom) - 1):
        _eta = [0, 0]
        xba = geom[i + 1][0] - geom[i][0]
        yba = geom[i + 1][1] - geom[i][1]
        if flip_n:
            yba = -yba
            xba = -xba
        nrm2 = math.sqrt(yba ** 2 + xba ** 2)
        if nrm2 == 0:
            _eta[0] = yba / nrm2
            _eta[1] = -xba / nrm2
            Logger.warning(f"eta = {eta}, norm = {nrm2}, geom = {geom}")
        else:
            _eta[0] = yba / nrm2
            _eta[1] = -xba / nrm2
        eta.append(_eta)
    # last point (a somewhat simplistic approach)
    eta.append(eta[-1])
    return eta


def normals_2d_np(geom: np.array, flip_n=False, show_norms=False):
    eta = np.ndarray((len(geom) - 1, 2))
    for i in range(len(geom) - 1):
        xba = geom[i + 1, 0] - geom[i, 0]
        yba = geom[i + 1, 1] - geom[i, 1]
        if flip_n:
            yba = - yba
            xba = - xba
        nrm2 = np.sqrt(yba ** 2 + xba ** 2)
        if nrm2 == 0:
            Logger.warning(f"eta = {eta}, norm = {nrm2}, geom = {geom}")
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
