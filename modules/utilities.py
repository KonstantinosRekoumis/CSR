import math
import colorama as clrm

'''
UTILITIES Module
Utilities module contains various convenience functions
'''
_WARNING_ = clrm.Back.YELLOW+clrm.Fore.RED
_SUCCESS_ = clrm.Back.GREEN+clrm.Fore.BLACK
_INFO_ = clrm.Back.YELLOW+clrm.Fore.BLUE
_ERROR_ = clrm.Back.RED+clrm.Fore.WHITE
_RESET_ = clrm.Style.RESET_ALL

_TITLE_ = clrm.Fore.RED

def d2r(x):
    return x/180*math.pi
def c_warn(*text,default = True):
    print(_WARNING_,"-- !! WARNING !! --\n",*text,_RESET_) if default else print(_WARNING_,*text,_RESET_)

def c_error(*text,default = True):
    print(_ERROR_,*text,_RESET_) if default else print(_ERROR_,*text,_RESET_)

def c_success(*text,default = True):
    print(_SUCCESS_,"-- !! SUCCESS !! --\n",*text,_RESET_) if default else print(_SUCCESS_,*text,_RESET_)

def c_info(*text,default = True):
    print(_INFO_,"-- ! INFO ! --\n",*text,_RESET_) if default else print(_INFO_,*text,_RESET_)

def linear_inter(start,end,target_x) -> float:
    '''
    y_target = (y_end-y_start)/(x_end-x_start)*(target_x-x_start)
    '''
    return (end[1]-start[1])/(end[0]-start[0])*(target_x-start[0])

def lin_int_dict(dict:dict,key:float,*f_args,suppress = False) -> float:
    '''
    Parses a dictionary of values and linear interpolates at key value accordingly
    '''
    #checks whether the function is presented to proper data
    try:
        for i in dict:
            if not(type(i) ==float or type(i) ==int): 
                c_warn(i,dict[i])
                raise KeyError
            else:
                if not(type(dict[i])==float or type(dict[i])==int): 
                    if callable(dict[i]) :
                        if not suppress:
                            c_warn("Detected a function. May result in error...")
                            c_warn(dict[i])
                    else:
                        c_warn(i,dict[i])
                        raise KeyError
    except KeyError:
        c_error("Input dictionary expects both the keys and their values to be of type float or int.\nThus the program terminates....")
        quit()

    out = 0
    if key in dict:
        out = dict[key]
    else :
        tmp_x = [0,0] #first position holds the maximum minimum and the second position the minimum maximum
        tmp_y = [0,0] #first position holds the maximum minimum and the second position the minimum maximum
        for i in dict:
            if key > i and  i > tmp_x[0]:
                tmp_x[0] = i 
                tmp_y[0]=dict[i] if not callable(i) else i(*f_args)
            elif key < i and i < tmp_x[0]:
                tmp_x[1] = i 
                tmp_y[1]=dict[i] if not callable(i) else i(*f_args)
        out = linear_inter((tmp_x[0],tmp_y[0]),(tmp_x[1],tmp_y[1]),key)
    return out

def linespace(start:int,end:int,step:int,skip=0):
    """
    A function that creates a linear space from start to end with step.
    skip = N -> skips every other N element
    """
    out =[]
    if skip !=0:
        for i,j in enumerate(range(start,end,step)):
            if i%skip != 0 and skip !=0:
                out.append(j)
    else:
        out = [i for i in range(start,end,step)]
    return out