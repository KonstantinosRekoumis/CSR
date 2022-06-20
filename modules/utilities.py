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

def linear_inter(start,end,target_x) -> float:
    '''
    y_target = (y_end-y_start)/(x_end-x_start)*(target_x-x_start)
    '''
    return (end[1]-start[1])/(end[0]-start[0])*(target_x-start[0])

def lin_int_dict(dict:dict,key:float) -> float:
    '''
    Parses a dictionary of values and linear interpolates at key value accordingly
    '''
    #checks whether the function is presented to proper data
    try:
        for i in dict:
            if type(i)!=float or type(i)!=int: raise KeyError
            else:
                if type(dict[i])!=float or type(dict[i])!=int: 
                    if type(dict[i]) == function:
                        c_warn("Detected a function. May result in error...")
                    else:
                        raise KeyError
    except KeyError:
        c_error("Input dictionary expects both the keys and their values to be of type float or int.\nThus the program terminates....")
        quit()

    out = 0
    if key in dict:
        out = dict[key]
    else :
        tmp = [0,0] #first position holds the maximum minimum and the second position the minimum maximum
        for i in dict:
            if key > i and  i > tmp[0]:
                tmp[0] = i
            elif key < i and i < tmp[0]:
                tmp[1] = i
        out = linear_inter((tmp[0],dict[tmp[0]]),(tmp[1],dict[tmp[1]]),key)
    return out