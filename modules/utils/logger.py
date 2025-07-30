import inspect
import os
import sys
from datetime import datetime

from modules.utils.colours import LogLevelColours, Colours


class Logger:
    LEVEL = 2
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
        Logger.error("Cannot instantiate static class!")

    @staticmethod
    def success(*args):
        print(Logger.get_prefix(LogLevelColours.SUCCESS, "SUCCESS"), *args, f"{Colours.NOCOLOUR}", file=Logger.OUT)

    @staticmethod
    def info(*args):
        print(Logger.get_prefix(LogLevelColours.INFO, "INFO"), *args, f"{Colours.NOCOLOUR}", file=Logger.OUT)

    @staticmethod
    def debug(*args):
        if Logger.LEVEL < 4:
            return
        print(Logger.get_prefix(LogLevelColours.DEBUG, "DEBUG"), *args, f"{Colours.NOCOLOUR}", file=Logger.OUT)

    @staticmethod
    def warning(*args):
        if Logger.LEVEL < 2:
            return

        print(Logger.get_prefix(LogLevelColours.WARNING, "WARNING"), *args, f"{Colours.NOCOLOUR}", file=Logger.OUT)

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
        print(Logger.get_prefix(LogLevelColours.ERROR, "ERROR"), *args, f"{Colours.NOCOLOUR}", file=Logger.OUT)
        # noinspection PyExceptionInherit
        if rethrow is not None:
            raise rethrow

        if die:
            raise RuntimeError(*args)

    @staticmethod
    def get_parent() -> str:
        return inspect.stack()[3][3]

    @staticmethod
    def get_file() -> str:
        return inspect.stack()[3][1].split(os.sep)[-1]

    @staticmethod
    def get_prefix(colour: LogLevelColours, name) -> str:
        return f"{colour}{datetime.now().strftime('%H:%M:%S')}|{name}|{Logger.get_file()}|{Logger.get_parent()} :"
