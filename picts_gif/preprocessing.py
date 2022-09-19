import numpy as np
from scipy.optimize import root
import pandas as pd


def create_t1_values (t1_min, t1_shift, n_windows,):
    '''
    Creates the set of t1 values that represent the first gates of all rate windows.\n\n
    t1_min: minimum value of t1\n
    t1_shift: for the linear method it represents the "delta t" between one gate and the next\n
    n_windows: nuber of rate windows, i.e. number of t1 values of the returned array. If it's not passed, the max number of windows for the transient is automatically generated. In this case, tr needs to be passed. \n
   
    Returns:
    numpy array with all t1 values.
    '''
    t1 =  np.array([t1_min+t1_shift*i for i in range(n_windows)])        
    return t1

def en_2gates_high_injection (en, t1, t2):
    '''
    The roots of this function gives the value of en for a given t1 and t2.
    This is a trascendental equation with 2 solutions. One solution is 0, the other is the real value of en.
    For reference see Balland et al. 1984 part II and Supporting info of Pecunia et al. 2021.
    '''
    return np.exp(en*(t2-t1)) - ( (1-en*t2)/(1-en*t1))

def calculate_en (t1, t2):
    '''
    Returns the rate window values starting from the gate values. It numerically solves the related equation
    t1: numpy array coontaining values of the 1st gate \n
    t2: numpy array containing values for the second gate \n
    
    Returns: a numpy array with the rate window values
    '''
  
    en = np.array([])
    for t1, t2 in zip(t1,t2):
        en_guess = 1/(t2-t1)*(t2/t1)    
        # As a guess we use this, which seems to work well (totally empiric, 1/(t2-t1) alone sometimes does not work). 
        #The problem is we need to choose a starting point that is closer to our searched value than to 0, 
        # otherwise the function will return the 0 value as result.
        # We use the root function from scipy.optimize to numerically solve
        en = np.append(en, root(en_2gates_high_injection, x0=en_guess, args=(t1, t2)).x)
    return en


    



