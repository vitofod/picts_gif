from nptdms import TdmsFile
import numpy as np
from scipy.optimize import root
import pandas as pd

def convert_tdms_file_to_dataframe(path, data_group_name):
    '''
    This method convert a tdms file to a dataframe. 
        .....................................................
        ......................................................

         Input parameters:
         - path: 
            string with file path of TDMS file
         - data_group_name: 
            the string key in wich data are stored in TDMS file. 
        
        ......................................................
         Return:
         - dataframe in wich are stored current transient in function of temperature. 
        ......................................................
        ......................................................
    '''
    # Import the file with the Tdms libraries
    tdms_file = TdmsFile.read(path)
    # Within the tdms_file object, the acquired data is found in 'Measured Data'.
    # This option is not universal, but specific to our data acquisition system.
    data = tdms_file[data_group_name].as_dataframe()
    #info about the starting index due to the trigger
    # LabVIEW program saves in 'wf_trigger_offset' info of the LED trigger
    data.index = tdms_file[data_group_name].channels()[0].time_track()
    trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']  
    data.index -= trigger
    return data

def set_column_and_index_name(data, dic_name):
    '''
    This method sets the name of index and column of a dataframe. 
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the dataframe
         - dic_name: 
            dictionary with index and column name. 
        
        ......................................................
         Return:
         - dataframe with column and index name setted . 
        ......................................................
        ......................................................
    '''
    # I arrange the labels of the columns. The acquisition system provides a standard name of the type 'wf_ <temperature value>'. 
    # For convenience, I want the name of the columns to coincide with the value of the temperature at which the current transient was measured.
    data.columns = [float(temp.replace('wf_','')) for temp in data.columns]
    data.columns.name = dic_name['columns_name']
    data.index.name = dic_name['index_name'] #Rename the index
    # I want to set the index (the time, it will be my x-axis) and arrange the x-axis so that the zero of my reference system coincides 
    # with the LED turning off. 
    # The moment the LED turns off is recorded in the Tdms file, as it is used as a trigger for the acquisition of the measurement.
    # Take index from the first channel, it should be the same for all channels (i.e.) temperatures. 
    return data

def set_current_value(data, gain):
    '''
    This method sets the proper values of current. 
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the dataframe
         - gain: 
            the moltiplicatory factor of the current amplifier. 
        
        ......................................................
         Return:
         - dataframe with proper current value. 
        ......................................................
        ......................................................
    '''
    # set the correct value of the current. 
    #check amplifier_gain > 0
    if gain < 0:  raise ValueError('In set_amplifier_gain: Not appropiate value.')
    transient = data/gain 
    return transient 

def check_and_fix_trigger_value_if_corrupted(data, trigger_value):
    '''
    This method check if the index zero coincide with trigger data. If not,
    sets the proper value. 
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the dataframe
         - trigger_value: 
            the time respect the index values in wich trigger starts. 
        
        ......................................................
         Return:
         - dataframe with proper start trigger value. 
        ......................................................
        ......................................................
    '''
    #It is possible that the trigger data that sets the zero of the transient is corrupted. 
    # If the data is corrupted, set zero from the configuration file. 
    if trigger_value != 'auto':
        data.index -= data[trigger_value].diff().idxmin() #the zero is positioned exactly in 
                                                                    #the minimum of the derivative 
                                                                    # (this is due to the shape of the signal)
    return data 



def create_t1_and_t2_values (t1_min, t1_shift, n_windows, beta):
    '''
    Creates the set of t1 and t2 values that represent the first gates of all rate windows.
        .....................................................
        ......................................................

         Input parameters:
         - t1_min: 
            minimum value of t1
         - t1_shift:
            represents the "delta t" between one gate and the next
         - n_windows:
            nuber of rate windows
        
        ......................................................
         return:
         t1:
            - numpy array with all t1 values.
         t2:
            - numpy array with all t2 values.
        ......................................................
        ......................................................
    '''
    t1 =  np.array([t1_min+t1_shift*i for i in range(n_windows)])      
     # Create t2 based on t1 and beta
    t2 = np.array([beta*t1 for t1 in t1])
    #if (t2>transient_norm.index.max()).any():      # If any value in t2 is bigger than the maximum time of the transients
        #raise ValueError('Some t2 values are bigger than the highest value of the transient time index. Adjust your t1 and beta accordingly.')  
    return t1, t2

def create_index_for_t1_and_t2(transient_norm, t1, t2):
    '''
    This method return an enumeration for the values in t1 and t2.
        .....................................................
        ......................................................

         Input parameters:
         - transient_norm:
            the dataframe of the normalized transient
         - t1: 
            numpy array with t1 values
         - t2:
            numpy array with t2 values
        ......................................................
         return:
         t1_index:
            - numpy array with all t1 values.
         t2_index:
            - numpy array with all t2 values.
        ......................................................
        ......................................................
    '''
     # location of t1 values. needed for using iloc later since loc has problems with tolerance
    #This method allows you to enumerate the values ​​of the indexes (which are floats with many digits after the comma).
    # In this way, the first index corresponds to 1, the second to 2, etc., etc.
    
    t1_index = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t1])    
    t2_index = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t2])    # location of t2 vcalues
    return t1_index, t2_index

def en_2gates_high_injection (en, t1, t2):
    '''
    The roots of this function gives the value of en for a given t1 and t2.
    This is a trascendental equation with 2 solutions. One solution is 0, the other is the real value of en.
    For reference see Balland et al. 1984 part II and Supporting info of Pecunia et al. 2021.
    .....................................................
    ......................................................

         Input parameters:
         - en: 
            rate window value
         - t1_shift:
            it represents the "delta t" between one gate and the next
         - t2:
            numpy array containing values for the second gate
            
        
        ......................................................
         Return:
         - the float solution of the expression
        ......................................................
        ......................................................
    '''
    return np.exp(en*(t2-t1)) - ( (1-en*t2)/(1-en*t1))

def calculate_en (t1, t2):
    '''
    Returns the rate window values starting from the gate values. It numerically solves the related equation
    For reference see Balland et al. 1984 part I and II and Supporting info of Pecunia et al. 2021.
    .....................................................
    ......................................................

         Input parameters:
         - t1: 
            numpy array containing values for the first gate
         - t2:
            numpy array containing values for the second gate
            
        ......................................................
         Return:
         - a numpy array with the rate window values
        ......................................................
        ......................................................
    '''
  
    en = np.array([])
    for t1, t2 in zip(t1,t2):
        #The problem is to choose a starting point that is closer to our searched value than to 0, 
        # otherwise the function will return the 0 value as result. I use this suggested expression 
        # from Supporting info of Pecunia et al. 2021.
        en_guess = 1/(t2-t1)*(t2/t1)    
        
        
        # I use the root function from scipy.optimize to numerically solve
        en = np.append(en, root(en_2gates_high_injection, x0=en_guess, args=(t1, t2)).x)
    return en


    


