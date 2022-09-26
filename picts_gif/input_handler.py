import pandas as pd
import numpy as np
from picts_gif import utilities
import json

import matplotlib.pyplot as plt 
class InputHandler:
    '''
    This class allows the reading and manipulation of TDMS type files specific to PICTS experiments or from other input
    '''
    def __init__(self):
        pass
    
    @staticmethod
    def read_transients_from_tdms(path, configuration_path, data_group_name = 'Measured Data'):
        '''
         This method transforms a TDMS file into a data frame.
         The dataframe contains current transients with time as index and temperature as columns.
         .....................................................   
         .....................................................

         The input parameters are:
         - path: 
            string with file path of TDMS file
         - configuration_path:
            path to a json file with all needed information to analyze the input data.
            This information comes from a preliminary data analysis done with the data 
            acquisition software in LabVIEW
         - data_group_name: 
            the string key in wich data are stored in TDMS file. 'Measured Data' by defaoult
        
         ......................................................
         Return:
         - a dataframe in wich are stored current transient in function of temperature. 
         ......................................................
         ......................................................
        '''
        #open the json parameters file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        # Import the file with the Tdms libraries
        # Within the tdms_file object, the acquired data is found in 'Measured Data'.
        # This option is not universal, but specific to our data acquisition system.
        #becouse a problem in data acquisition software (LabVIEW) the data transient stored are inverted 
        #To have the proper data, i have to return the inverted dataframe
        data = -utilities.convert_tdms_file_to_dataframe(path, data_group_name)
        #set column and index name
        dict_name = {
                    'index_name': 'Time (s)',
                    'columns_name': 'Temperature (K)'
                    }
        data = utilities.set_column_and_index_name(data, dict_name)
        # set the correct value of the current. 
        #check amplifier_gain > 0
        data = utilities.set_current_value(data, configuration['gain'])
        #set the zero in x-axis
        
        data = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(data, configuration['set_zero'])
        #some trim of data
        if (configuration['trim_left'] != None  and configuration['trim_right'] != None):
            left_index_cut = configuration['trim_left']
            right_index_cut = configuration['trim_right']
            data = utilities.trim_dataframe(data, left_index_cut, right_index_cut)
       
        return data 

    @staticmethod
    def read_transients_from_pkl(path):
         '''
         This method transforms a.pkl into a data frame.
         Dataframe containing current transients with time as index and temperature as columns
         .....................................................
         .....................................................

         The input parameters are:
         - path: 
            string with file path of TDMS file
         ......................................................
         Return:
         - a dataframe in wich are stored current transient in function of temperature. 
         ......................................................
         ......................................................
        '''
         if '.pkl' in path: 
            return pd.read_pickle(path,'bz2')   

    def normalized_transient(transient, configuration_path):
        '''
         This method normalized the raw transient dataframe input from 'read_transient_from_*'.
         .....................................................
         .....................................................

         The input parameters are:
         - data: 
            transient dataframe to normalize    
         - configuration_path:
            path to a json file with all needed information to analyze the input data.
            This information comes from a preliminary data analysis done with the data 
            acquisition software in LabVIEW
        
         ......................................................
         Return:
         - normalized_transient:
             a dataframe in wich are stored normalized current transient in function of temperature, 
             with time as index and temperature as columns.
         ......................................................
         ......................................................
        '''
        #open the json parameters file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
        #normalized the current transient
        #recover the values ​​of the dark current
        i_dark_range = [configuration['i_dark_left'], configuration['i_dark_right']]
        #recover the values ​​of the light current
        i_light_range = [configuration['i_light_left'], configuration['i_light_right'] ]
        #the value of the light and dark currents are the averages of the values ​​of the currents in the assigned ranges
        i_light = transient.loc[i_light_range[0]:i_light_range[1]].mean()
        i_dark = transient.loc[i_dark_range[0]:i_dark_range[1]].mean()
       # print(i_light, i_dark)
       # if i_light.iloc[0:1] < i_dark.iloc[0:1]:  raise ValueError('In normalized_transient: i_light smaller than i_dark.')
        transient_norm = (transient-i_dark)/(i_light-i_dark)
       # plt.title("transient_norm")
        return transient_norm

    @staticmethod
    def from_transient_to_PICTS_spectrum (transient_norm, configuration_path):
        '''
         This method transforms the normalized_transient dataframe into a dataframe containing the PICTS spectrum.
         Dataframe have temperature as index and rate window as columns
         .....................................................
         .....................................................

         The input parameters are:
         - data: 
            dataframe to analyze    
         - parameters_path:
            path to a json file with all needed information to analyze the input data
        
         ......................................................
         Return:
         - picts:
            a dataframe with the picts spectrum, with temperature as index and 'rate window' as columns.    
         - gates:
            a list of pair float. Each pair represent a rate window
         ......................................................
         REFERENCES:
         For a better understanding of what a PICTS spectrum is and what a rate window represents see:
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 57
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 71  
          - Pecunia et al. 2021, Adv. Energy Mater. 2021, 11, 2003968 with emphasis on Supporting Info
         ......................................................
         ......................................................
        '''
        
        
        #open the json parameters file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
        

        #I calculate the values ​​of t1 and t2
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        
        
        # location of t1 values. needed for using iloc later since loc has problems with tolerance
        #This method allows you to enumerate the values ​​of the indexes (which are floats with many digits after the comma).
        # In this way, the first index corresponds to 1, the second to 2, etc., etc.
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(transient_norm, t1, t2)
        

        # Calculate rate windows.
        en = utilities.calculate_en(t1, t2 = configuration['beta']*t1)
        # Calculate picts signal for each rate window 
        picts = pd.concat(
                          [transient_norm.iloc[t1-configuration['t_avg']:t1+configuration['t_avg']].mean() 
                          - transient_norm.iloc[t2-configuration['t_avg']:t2+configuration['t_avg']].mean() \
                          for t1,t2 in zip(t1_index,t2_index)], 
                          axis=1
                          )
        
        #I put in order index and columns
        picts.index=picts.index.astype(float)
        picts.columns = en.round(3)
        picts.columns.name = 'Rate Window (Hz)'
        gates = np.array([t1, t2]).T       # I traspose it so that each row corresponds to a rate window

        
        return  picts, gates


if __name__ == "__main__":
    
    path = '/home/vito/picts_gif/tests/test_data/data.tdms'
    dic_path = '/home/vito/picts_gif/tests/test_data/dictionary.json'
    
    
    transient = InputHandler.read_transients_from_tdms(path, dic_path)
    normalized_transient = InputHandler.normalized_transient(transient, dic_path)
    picts, gates = InputHandler.from_transient_to_PICTS_spectrum(normalized_transient, dic_path)
     
    #print('data',transient.head())
    #print('transient',normalized_transient.head())
    #print('picts',picts.head())
    #print('gates',gates)
    picts.plot()
    plt.show()
    #transient[90.768].plot()
    #plt.show()
    #normalized_transient[90.768].plot()
    #plt.show()

   

# TODO risistemare InputHandler che gestisca anche altri tipi di input. Separare preprocessamento dei dati in un' altra classe