import math
import colorama

"""
UTILITIES Module
Utilities module contains various convenience functions
"""

# FIXME move all of this in an enum
WARNING = colorama.Back.YELLOW + colorama.Fore.RED
SUCCESS = colorama.Back.GREEN + colorama.Fore.BLACK
INFO = colorama.Back.YELLOW + colorama.Fore.BLUE
ERROR = colorama.Back.RED + colorama.Fore.WHITE
RESET = colorama.Style.RESET_ALL

TITLE = colorama.Fore.RED


def d2r(x):
    return x / 180 * math.pi


def c_warn(*text, default=True):
    print(WARNING, "-- !! WARNING !! --\n", *text, RESET) if default else print(WARNING, *text, RESET)


def c_error(*text, default=True):
    print(ERROR, *text, RESET) if default else print(ERROR, *text, RESET)


def c_success(*text, default=True):
    print(SUCCESS, "-- !! SUCCESS !! --\n", *text, RESET) if default else print(SUCCESS, *text, RESET)


def c_info(*text, default=True):
    print(INFO, "-- ! INFO ! --\n", *text, RESET) if default else print(INFO, *text, RESET)


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
            if not (i is float or i is int):
                c_warn(i, vli_dict[i])
                raise KeyError
            else:
                if not (vli_dict[i] is float or vli_dict[i] is int):
                    if callable(vli_dict[i]):
                        if not suppress:
                            c_warn("Detected a function. May result in error...")
                            c_warn(vli_dict[i])
                    else:
                        c_warn(i, vli_dict[i])
                        raise KeyError
    except KeyError:
        c_error(
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
