from nptdms import TdmsFile
import numpy as np
from scipy.optimize import root
import pandas as pd

def convert_tdms_file_to_dataframe(
    path : str, 
    data_group_name : str
    ) -> pd.DataFrame :
    '''
    This method convert a tdms file in a dataframe. 
        .....................................................
        ......................................................

         Input parameters:
         - path: str
            string with file path of TDMS file
         - data_group_name: str
            the string key in wich data are stored in TDMS file. 
        
        ......................................................
         Return:
         - data: pd.Dataframe
            dataframe in wich are stored current transient in function of temperature. 
         ......................................................
         REFERENCES:
         For a better understanding about tdms file format:
          - https://www.ni.com/it-it/support/documentation/supplemental/06/the-ni-tdms-file-format.html 
         ......................................................
         ......................................................
    '''
   
    tdms_file = TdmsFile.read(path)
    
    # Within the tdms_file object, the acquired data is found in 'Measured Data'.
    # This option is not universal, but specific to our data acquisition system.
    data = tdms_file[data_group_name].as_dataframe()
    
    #info about the starting index due to the trigger
    #The tdms file contains current transients as a function of time and temperature. 
    #Basically there is a thermal ramp that goes from T_min to T_max, and each T_x acquires a current transient as a function of time.
    data.index = tdms_file[data_group_name].channels()[0].time_track()   #this syntax is due to the structure of the tdms files. It's a bit tricky. 
                                                                         #The acquisition time is independent of the temperature. It will be the index of my dataframe.
                                                                         
    trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']  # LabVIEW program saves info about LED trigger in 'wf_trigger_offset'. 
                                                                                        #I need this because, to simplify the data analysis, 
                                                                                        # I need to fix a zero in my time frame. 
                                                                                        # The best thing to do is to fix zero exactly when the LED goes out.
    data.index -= trigger
    return data

###############################################################################################################################################################
###############################################################################################################################################################

def set_column_and_index_name(
    data : pd.DataFrame
    ) -> pd.DataFrame:
    '''
    This method sets the name of index and column of a dataframe. 
        .....................................................
        ......................................................

         Input parameters:
         - data: pd.Dataframe
            the input dataframe
         
        .....................................................
         Return:
         - data: pd.Dataframe
            dataframe with column and index name setted. 
        ......................................................
        ......................................................
    '''
    # I arrange the labels of the columns. The acquisition system provides a standard name of the type 'wf_ <temperature value>'. 
    # For convenience, I want the name of the columns to coincide with the value of the temperature at which the current transient was measured.
   
    data.columns = [float(temp.replace('wf_','')) for temp in data.columns] 
    data.columns.name = 'Temperature (K)'
    data.index.name = 'Time (s)' 
     
    return data

###############################################################################################################################################################
###############################################################################################################################################################

def set_current_value(
    data : pd.DataFrame, 
    gain : int
    ) -> pd.DataFrame:
    '''
    This method sets the proper value of current. 
    The current values ​​acquired by the software are those in output from an operational amplifier. 
    Knowing the gain of the amplifier, I can set the correct current values.
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the current transient dataframe
         - gain: 
            the moltiplicatory factor of the current amplifier. 
        
        ......................................................
         Return:
         - data: pd.Dataframe
            dataframe with proper current value. 
        ......................................................
         Raises
         - ValueError
            If gain value is equal or smaller than zero.
        ......................................................
        ......................................................
    '''
    if gain <= 0: raise ValueError('Gain must be > 0')
    return data/gain  

###############################################################################################################################################################
###############################################################################################################################################################

def check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(
    data : pd.DataFrame, 
    index : int
    ) -> pd.DataFrame:
    '''
    This method check if the zero of the time index coincide with the drop of the current. If not,
    it fixs index value. 
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the current transient dataframe
         - index: 
            the index respect to calculate new zero of time reference. 
        
        ......................................................
         Return:
         - dataframe with proper zero of time reference. 
        ......................................................
        ......................................................
    '''
    # I want that the index (the time, it is my x-axis) have a proper zero in reference system, 
    # that coincides with the LED turning off. 
    # The moment the LED turns off is recorded in the Tdms file, as it is used as a trigger for the acquisition of the measurement.
    # I taked it when i call the methods set_column_and_index_name
    
    #It is possible that the trigger data that sets the zero of the transient is corrupted (this is due to a bug in LabVIEW software). 
    #If the data is corrupted, with this method i set the zero following a different way. 
    
    #Since I want the zero of my time axis to coincide with the LED turning off (and therefore with the current drop), 
    #what I have to look for is the instant in which the derivative of the transient has a minimum.
    #The zero is positioned exactly in the minimum of the derivative
    #of the current transient (this is due to the shape of the signal)

    if index != 'auto':
        data.index -= data.iloc[:,index].diff().idxmin() 
    return data 

###############################################################################################################################################################
###############################################################################################################################################################

def trim_dataframe(
    data : pd.DataFrame, 
    left_cut : int, 
    right_cut : int
    ) -> pd.DataFrame:
    '''
    This method reduces the extension of the rows of the dataframe. 
    The starting data indicates how many starting lines to cut and how many ending lines to cut 
        .....................................................
        ......................................................

         Input parameters:
         - data: 
            the dataframe
         - left_cut: 
            index value.
         - right_cut: 
            index value.  
        
        ......................................................
         Return:
         - dataframe trimmed. 
        ......................................................
         Raises
         - ValueError
            If left_cut index is bigger than right_cut index
        ......................................................
        ......................................................
    '''
    if left_cut > right_cut: raise ValueError('Left index must be smaller than the right one')
    return data.loc[:,left_cut:right_cut]
    
###############################################################################################################################################################
###############################################################################################################################################################


def create_t1_and_t2_values (
    t1_min : float, 
    t1_shift : float, 
    n_windows : int, 
    beta : float
    ) -> np.array :
    '''
    Creates the set of t1 and t2 values.
        .....................................................
        ......................................................

         Input parameters:
         - t1_min: 
            minimum value of t1
         - t1_shift:
            represents the "delta t" between one gate and the next
         - n_windows:
            nuber of rate windows
         - beta: the proportionality constant between t1 and t2
        
        ......................................................
         return:
         t1:
            - numpy array with all t1 values.
         t2:
            - numpy array with all t2 values.
        ......................................................
        ......................................................
    '''
    #create t1 value starting from some parameters. these parameters were chosen 
    #on the basis of a previous analysis of the signal in LabVIEW   
    
    #t1 is chosen so that the elements of the array are in linear relationship to each other. 
    #There is no reason to think that this method is better than others. The only condition is that the created values ​​are monotonous increasing
    t1 =  np.array([t1_min+t1_shift*i for i in range(n_windows)])      
     # Create t2 based on t1 and beta
    t2 = np.array([beta*t1 for t1 in t1])
   
    return t1, t2

###############################################################################################################################################################
###############################################################################################################################################################

def create_index_for_t1_and_t2(
    transient_norm : pd.DataFrame, 
    t1 : np.array, 
    t2 : np.array
    ) -> np.array:
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
            - numpy array with the enumeration of t1 values.
         t2_index:
            - numpy array with the enumeration of t2 values.
        ......................................................
        ......................................................
    '''
    #Needed for using iloc later since iloc has problems with tolerance
    #This method allows us to enumerate the values ​​of the indexes (which are floats with many digits after the comma).
    #In this way, the first index corresponds to 1, the second to 2, etc., etc.
    
    t1_index = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t1])    
    t2_index = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t2])    
    return t1_index, t2_index

###############################################################################################################################################################
###############################################################################################################################################################

def en_2gates_high_injection (
    en : np.array, 
    t1 : np.array, 
    t2 : np.array
    ):
    '''
    This methods return the relation between en and (t1, t2).
    .....................................................
    ......................................................

         Input parameters:
         - en: 
            rate emission value
         - t1:
            numpy array containing values for the first gate
         - t2:
            numpy array containing values for the second gate
            
        
        ......................................................
         Return:
         - a trascendental equation
        ......................................................
         REFERENCES:
         For a better understanding about the relation between e_n and (t1, t2) see:
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 71  
          - Pecunia et al. 2021, Adv. Energy Mater. 2021, 11, 2003968 with emphasis on Supporting Info
          
          You also can see EXTRA in README.md
         ......................................................
         ......................................................
    '''
    #The theory behind which the PICTS technique was developed 
    # gives us a relationship between the emission rate en and the values ​​t1 and t2 of the selected rate window
    return np.exp(en*(t2-t1)) - ( (1-en*t2)/(1-en*t1))

###############################################################################################################################################################
###############################################################################################################################################################

def calculate_en (
    t1 : np.array, 
    t2 : np.array
    ) -> np.ndarray:
    '''
    Returns a numpy array with en values, starting from the rate window values. 
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
         REFERENCES:
         For a better understanding about the relation between e_n and (t1, t2) see:
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 71  
          - Pecunia et al. 2021, Adv. Energy Mater. 2021, 11, 2003968 with emphasis on Supporting Info
         ......................................................
         ......................................................
    '''
    #It numerically solves the related trascendental equation returned from 
    #en_2gates_high_injection. This equation have two solution: one is zero, the other is the real value of en.
    #Zero solution is the bad one.
  
    en = np.array([])
    for t1, t2 in zip(t1,t2):
        #The problem is to choose a starting point for en that is closer to our searched value than to 0, 
        # otherwise the function will return the 0 value as result. I use the "low injection" expression for en, 
        # see Supporting info of Pecunia et al. 2021. I chose this expression because it returns
        # an approximate value ​​of en, the so-called 'low injection', close to the real one. 
        en_guess = 1/(t2-t1)*(t2/t1)    
        
        
        # I use the root function from scipy.optimize to numerically solve
        en = np.append(en, root(en_2gates_high_injection, x0=en_guess, args=(t1, t2)).x)
    return en


    



