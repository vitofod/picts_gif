import numpy as np
from scipy.optimize import root
import pandas as pd

def set_amplifier_gain(df, amplifier_gain):
        '''
        This method attributes the correct amplification factor to the current transients,\n 
        so that the currents read are the real ones. The method takes a dataframe as input and returns a dataframe.
        .....................................................

        The input parameters are:
        - df: 
            the raw dataframe
        - amplifier_gain:
            the gain value set on the current amplificator 
        '''
        #check amplifier_gain > 0
        if amplifier_gain < 0:  raise ValueError('In set_amplifier_gain: Not appropiate value.')
        # Current values
        df=df/amplifier_gain                # Convert to current
        return df  

def optimize_dataframe(df, dropna=False, drop=None):
        '''
        This method to make some manipulation to the dataframe. 
        The method takes a dataframe as input and returns a dataframe.
        .....................................................

        The input parameters are:
        - df: 
            the raw dataframe
        - dropna:
            whether to drop all rows where there is at least one NaN. 
            Useful for faulty dataset where there are some columns with more data than others
        -   drop: 
            list of 2 integers indicating the initial and final columns to be dropped from the dataframe as soon as it is imported. 
            Usually used to remove the first or last columns which may contain corrupted data. If drop=[0,5] drop the first 4 columns\n
        '''
        if dropna: df=df.dropna()
        if drop is not None: df = df.drop(axis=1, columns = df.columns[drop[0]:drop[1]]) 
        return df

def set_zero_at_trigger(df, temperature):
        '''
        This method set the zero of the reference frame when led off.
        ...............................................................

        Input
            - df: 
                dataframe
            - temperature: 
                the float index temperature where take trigger values
        Output
            - df: 
                dataframe
        '''
        if temperature < 0:   raise ValueError('In set_zero_at_trigger: Not appropiate value.')
        df.index -= df[temperature].diff().idxmin()
        return df 

def normalized_transient(df, i_dark_range, i_light_range):
    '''
    This method normalized the current transient.
    ................................................................

    Input:
        - df:
            dataframe
        - i_dark_range: 
            a list of two float indicating the time interval in the current transient where to average the value of the dark current.
        - i_light_range:
            a list of two float indicating the time interval in the current transient where to average the value of the light current
    Output
        tr_norm:
            dataframe
    '''
    if i_dark_range[0] > i_dark_range[1]:  raise ValueError('In normalized_transient: i_dark_range problem.')
    if i_light_range[0] < i_dark_range[1]:  raise ValueError('In normalized_transient: i_light_range problem.')
    i_light = df.loc[i_light_range[0]:i_light_range[1]].mean()
    i_dark = df.loc[i_dark_range[0]:i_dark_range[1]].mean()
    tr_norm = (df-i_inf)/(i_0-i_inf)
    return tr_norm



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


def round_rate_window_values (df, en, round_value):
    '''
    df: input dataframe where columns are supposed to be en values\n
    en: rate window values\n
    round_value: decimal position en windows should be rounded to\n\n
    Returns:
    Dataframe with column values that are rate windows which have been rounded to the desired value.
    '''
    if round_value is None:
        df.columns = en
    else:
        if round_value>0: df.columns = en.round(round_value)
        elif (round_value==0): df.columns = en.round(0).astype(int)
        else :
            warnings.warn("Negative value of round_en! setting default values of rate windows", stacklevel=2)
            df.columns = en

    return df
         
            
    

def picts_2gates (tr, beta, t_avg, t1_min=None,  
                  t1_shift=None, n_windows=None,  integrate = False, 
                  round_en = None):
    '''
    tr: dataframe with transients at different temperatures\n
    t1_min: minimum value of t1. Necessary if t1 is not provided\n
    t1_shift: for the linear method it represents the "delta t" between one gate and the next
    n_windows: nuber of rate windows, i.e. number of t1 values of the returned array \n
    t1_method: method used to create t1 values. Accepted options are 'linear' (linearly increase the t1 values)
    t1: numpy array of values of t1, i.e. the first picts_2gates. VALUES IN SECONDS!\n
    beta: defined as t2/t1. t2 vcalues are obtained from this and t1\n
    t_avg: number of points to be averaged around t1 and t2. Not relevant if integrate=True. E.g. if t_avg=2, I average between i(t1) and the 2 points below and above, 5 in total. Same for i(t2).\n
    integrate: whether to perform double boxcar integration, i.e. calculating the integral of the current between t1 and t2 for each temperature (ref: Suppl. info of https://doi.org/10.1002/aenm.202003968 )\n
    round_en: integer indicating how many decimals the rate windows should should be rounded to. If None, the default calculated values of en are kept.\n
    injection: can be either "high" (default) or "low", corresponding to high or low injection from the light source. The expression for finding en is different in the 2 cases. \n
    Returns a dataframe with PICTS spectra and t2 values
    '''
    # Initial checks
    if (type(t1)!=np.ndarray and t1 is not None):
        raise TypeError('t1 must be numpy.ndarray object')
    # Create t1 values, if needed
    
    t1 = create_t1_values(t1_min, t1_shift, n_windows)
    if (t1>tr.index.max()).any():      # If any value in t1 is bigger than the maximum time of the transients
        raise ValueError('Some t1 values are bigger than the highest value of the transient time index')

    # Create t2 based on t1 and beta
    t2 = np.array([beta*t1 for t1 in t1])
    if (t2>tr.index.max()).any():      # If any value in t2 is bigger than the maximum time of the transients
        raise ValueError('Some t2 values are bigger than the highest value of the transient time index. Adjust your t1 and beta accordingly.')

    t1_loc = np.array([tr.index.get_indexer([t], method = 'backfill')[0] for t in t1])    # location of t1 values. needed for using iloc later since loc has problems with tolerance
    t2_loc = np.array([tr.index.get_indexer([t], method = 'backfill')[0] for t in t2])    # location of t2 vcalues
    # Calculate rate windows.
    #en = np.log(beta)/(t1*(beta-1))
    en = calculate_en(t1 = t1, t2 = beta*t1)
    # Calculate picts signal for each rate window taking the integral of the current between t1 and t2 
    
    picts = pd.concat([tr.iloc[t1-t_avg:t1+t_avg].mean() - tr.iloc[t2-t_avg:t2+t_avg].mean() \
                           for t1,t2 in zip(t1_loc,t2_loc)], axis=1)
    picts = round_rate_window_values(picts, en, round_en)
    picts.columns.name = 'Rate Window (Hz)'
    gates = np.array([t1, t2]).T       # I traspose it so that each row corresponds to a rate window
    
    return picts, gates

