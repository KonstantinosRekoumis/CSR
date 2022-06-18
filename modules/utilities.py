import colorama as clrm

'''
UTILITIES Module
Utilities module contains various convenience functions
'''
_WARNING_ = clrm.Back.YELLOW+clrm.Fore.RED
_ERROR_ = clrm.Back.RED+clrm.Fore.WHITE
_RESET_ = clrm.Style.RESET_ALL

def c_warn(text:str):
    print(_WARNING_,"-- !! WARNING !! --\n",text,_RESET_)

def c_error(text:str):
    print(_ERROR_,text,_RESET_)