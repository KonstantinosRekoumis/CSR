from enum import StrEnum


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