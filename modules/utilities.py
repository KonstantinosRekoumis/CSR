import math
import os
import sys
import inspect
from enum import StrEnum
from datetime import datetime
from importlib.resources.abc import Traversable
from io import TextIOWrapper
import importlib.resources as resources
from typing import Self, Iterator


class ColourCodes(StrEnum):
    BLACK = "0m"
    WHITE = "15m"
    BLUE = "27m"
    TURQUOISE = "30m"
    GREEN = "34m"
    CYAN = "36m"
    LIGHT_BLUE = "39m"
    PALE_GREEN = "42m"
    STEEL_BLUE = "39m"
    PURPLE = "93m"
    RED = "124m"
    MAGENTA = "127m"
    BROWN = "138m"
    LIGHT_MAGENTA = "163m"
    DARK_ORANGE = "166m"
    ORANGE = "172m"
    YELLOW = "178m"
    LIGHT_RED = "196m"


class EscapeCodes(StrEnum):
    PREFIX = "\033["
    FOREGROUND = "38;"
    BACKGROUND = "48;"
    INFIX = "5;"
    PFI = f"{PREFIX}{FOREGROUND}{INFIX}"
    PBI = f"{PREFIX}{BACKGROUND}{INFIX}"


class Colours(StrEnum):
    NOCOLOUR = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    BYELLOW = f"{EscapeCodes.PBI}{ColourCodes.YELLOW}"
    BGREEN = f"{EscapeCodes.PBI}{ColourCodes.GREEN}"
    BRED = f"{EscapeCodes.PBI}{ColourCodes.RED}"
    FRED = f"{EscapeCodes.PFI}{ColourCodes.RED}"
    FBLACK = f"{EscapeCodes.PFI}{ColourCodes.BLACK}"
    FBLUE = f"{EscapeCodes.PFI}{ColourCodes.BLUE}"
    FWHITE = f"{EscapeCodes.PFI}{ColourCodes.WHITE}"


class LogLevelColours(StrEnum):
    DEBUG = f"{Colours.BYELLOW}{Colours.FBLACK}"
    INFO = f"{Colours.BYELLOW}{Colours.FBLUE}"
    SUCCESS = f"{Colours.BGREEN}{Colours.FWHITE}"
    WARNING = f"{Colours.BYELLOW}{Colours.FRED}"
    ERROR = f"{Colours.BRED}{Colours.FWHITE}"


class Logger:
    LEVEL = 4
    OUT = sys.stderr

    LOG_LEVELS = {
        "NONE": 0,
        "ERROR": 1,
        "WARNING": 2,
        "DEBUG": 4,
    }

    try:
        LEVEL = LOG_LEVELS[os.environ["CSR_LOG_LEVEL"]]
    except KeyError:
        print(f"Couldn't set LOG_LEVEL from CSR_LOG_LEVEL environment! Continuing with LOG_LEVEL: {LEVEL}", file=OUT)

    def __init__(self):
        raise NotImplementedError

    @staticmethod
    def get_parent() -> str:
        return inspect.stack()[2][3]

    @staticmethod
    def get_file() -> str:
        return inspect.stack()[2][1].split(os.sep)[-1]

    @staticmethod
    def success(*args):
        print(f"{LogLevelColours.SUCCESS}{datetime.now().strftime('%H:%M:%S')}|SUCCESS|{Logger.get_file()}|{Logger.get_parent()}",
              *args,
              f"{Colours.NOCOLOUR}",
              file=Logger.OUT)

    @staticmethod
    def info(*args):
        print(f"{LogLevelColours.INFO}{datetime.now().strftime('%H:%M:%S')}|INFO|{Logger.get_file()}|{Logger.get_parent()}",
              *args,
              f"{Colours.NOCOLOUR}",
              file=Logger.OUT)

    @staticmethod
    def debug(*args):
        if Logger.LEVEL < 4:
            return
        print(f"{LogLevelColours.DEBUG}{datetime.now().strftime('%H:%M:%S')}|DEBUG|{Logger.get_file()}|{Logger.get_parent()}",
              *args,
              f"{Colours.NOCOLOUR}",
              file=Logger.OUT)

    @staticmethod
    def warning(*args):
        """
        Second-highest priority logging function.
        """
        if Logger.LEVEL < 2:
            return
        print(f"{LogLevelColours.WARNING}{datetime.now().strftime('%H:%M:%S')}|WARNING|{Logger.get_file()}|{Logger.get_parent()}",
              *args,
              f"{Colours.NOCOLOUR}",
              file=Logger.OUT)

    @staticmethod
    def error(*args, die=True, rethrow: Exception = None):
        """
        Highest-priority logging function.
        :param die: Whether to die or not upon calling this function. Useful for unexpected errors. Defaults to True.
        :param rethrow: Whether to rethrow the specified exception. Useful for error messages. Defaults to None.
        :raises RuntimeError: This is raised if die is set to True.
        """

        if Logger.LEVEL < 1:
            return
        print(f"{LogLevelColours.ERROR}{datetime.now().strftime('%H:%M:%S')}|ERROR|{Logger.get_file()}|{Logger.get_parent()}",
              *args,
              f"{Colours.NOCOLOUR}",
              file=Logger.OUT)
        # noinspection PyExceptionInherit
        if rethrow is not None:
            raise rethrow

        if die:
            raise RuntimeError(*args)


class FileNotOpenError(Exception):
    pass


# noinspection PyShadowingNames
class Resource:
    """
    Opens a read-only local resource located in the local /resources module.
    The resource will be automatically found based on its filename.

    If there's a filename conflict, for example there are files on different
    levels of directories with the same filename, in order to avoid conflicts,
    use the "module" parameter to specify the relative path from the top-level
    /resources folder.
    """

    def __init__(self, fname: str, module: str = "", binary: bool = False, **kwargs):
        """
        :param fname: Name of the file to open.
        :param module: The directory filter. Specify in "import" style, for example: "dir.subdir"
        :param binary: Whether to open the file in binary mode. Defaults to False
        :param kwargs: Kwargs to pass to file.open(mode, **kwargs)
        """

        self.fname = fname
        self.path = module
        self.bmode = binary
        # noinspection PyTypeChecker
        self.file_descriptor: TextIOWrapper = None
        self.kwargs = kwargs

    def __enter__(self) -> Self:
        directory_specifier = self.path.split(".") if self.path else None

        toplevel_resources_module = resources.files('resources')
        for resource in Resource.iterate_directory(toplevel_resources_module):
            if resource.name == self.fname:
                # filter if there's a filter defined
                if directory_specifier:
                    full_path = str(resource).split(os.sep)
                    resource_contents_index = full_path.index("resources") + 1  # shift to the right
                    relative_path = full_path[resource_contents_index:-1]
                    for specified_dir, relative_dir in zip(directory_specifier, relative_path):
                        print(specified_dir, relative_dir)
                        if specified_dir != relative_dir:
                            continue
                self.file_descriptor = resource.open("rb" if self.bmode else "r", **self.kwargs)
                break

        if not self.file_descriptor:
            raise FileNotFoundError

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_descriptor is None:
            raise RuntimeError("self.file_descriptor is none in __exit__?!")

        if not self.file_descriptor.closed:
            self.file_descriptor.close()

        self.file_descriptor = None

    @property
    def contents(self) -> TextIOWrapper:
        if self.file_descriptor is None:
            raise FileNotOpenError()

        # FIXME: this is hacky; it's better to just expose the methods rather than the entire object
        #  however I'm limited by the technology of my time (meaning, I just don't know how to do it)
        return self.file_descriptor

    @staticmethod
    def iterate_directory(directory: Traversable) -> Iterator[Traversable]:
        for file in directory.iterdir():
            # ignore module definition file
            if file.name == "__init__.py":
                continue

            if file.is_dir():
                # ignore autogenerated python cache directory
                if file.name == "__pycache__":
                    continue
                for resource in Resource.iterate_directory(file):
                    yield resource
                continue

            yield file

        # prevent StopIteration
        return


# Writing boilerplate code to avoid writing boilerplate code!
# https://stackoverflow.com/questions/32910096/is-there-a-way-to-auto-generate-a-str-implementation-in-python
def auto_str(cls):
    """Automatically implements __str__ for any class."""

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


def d2r(x):
    return x / 180 * math.pi


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


def normals_2d(geom, flip_n=False):
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
