import pandas as pd
import numpy as np
from picts_gif import utilities
import json

class InputHandler:
    '''
    This class allows the reading and manipulation of TDMS type files specific to PICTS experiments or from other input as .pkl
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
         - Pandas dataframe  
         ......................................................
         ......................................................
        '''
        #open the json configuration file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
            
        #Import the Tdms file 
        #The acquired data is found in 'Measured Data' in tdms file.
        #This option is not universal, but specific to our data acquisition system.
        #Becouse a problem in data acquisition software (LabVIEW), the data transient stored are inverted 
        #To have the proper data, i have to return the inverted dataframe
        #You can see the dataframe as a table in which index is the x-axis and each column
        # represent a y-axis. Dataframe contains hundreds of transient, i don't suggest you
        # to use 'data.plot()'. If you want to see a transient, a good choise could be the 
        # hvplot from holoviews. Or simply 'data[<column>].plot()'
        data = -utilities.convert_tdms_file_to_dataframe(path, data_group_name)
        
        #set column and index name
        dict_name = {
                    'index_name': 'Time (s)',
                    'columns_name': 'Temperature (K)'
                    }
        data = utilities.set_column_and_index_name(data, dict_name)
        
        # set the correct value of the current. 
        data = utilities.set_current_value(data, configuration['gain'])
        
        #set the zero in x-axis 
        #It is possible that the trigger data that sets the zero of the transient is corrupted.
        #Index dataframe is our x-axis. I want that the zero of the x-axis coincide with the drop of the current.
        #LabVIEW software sets the proper zero, but becouse an unknown bug, sometimes doesn't work. So we have to ceck it.
        data = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(data, configuration['set_zero'])
        
        #some trim of data. Data at low temperature are very noisy. And in animation i don't want to
        #show the entire data, only some part of interest. So let's do some pruning
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
         - a pandas Dataframe 
         ......................................................
         ......................................................
        '''
        #we can pass the data as .pkl. 
         if '.pkl' in path: 
            return pd.read_pickle(path,'bz2')   
    
    @staticmethod
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
             a pandas dataframe in wich are stored normalized current transient in function of temperature, 
             with time as index and temperature as columns.
         ......................................................
         ......................................................
        '''
        #The values of the transient could change a lot in function of temperature.
        #Bad thing for animation. normalizing avoids a lot of trouble
        
        #open the json configuration file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
        
        #for normalized the transient we want to know the value of dark current and light current
        #To be more precise, we don't take a single current value, but we take a range over which we average
        
        #recover the values ​​of the dark current in a range 
        i_dark_range = [configuration['i_dark_left'], configuration['i_dark_right']]
        #recover the values ​​of the light current in a range
        i_light_range = [configuration['i_light_left'], configuration['i_light_right'] ]
        
        #the value of the light and dark currents are the averages of the values ​​of the currents in the assigned ranges
        i_light = transient.loc[i_light_range[0]:i_light_range[1]].mean()
        i_dark = transient.loc[i_dark_range[0]:i_dark_range[1]].mean()
       
       #normalized the current transient
       #The expression in the numerator allows us to set the dark current value to zero
        transient_norm = (transient-i_dark)/(i_light-i_dark)
      
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
        #This method allows us to enumerate the values ​​of the indexes (which are floats with many digits after the comma).
        # In this way, the first index corresponds to 1, the second to 2, etc., etc.
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(transient_norm, t1, t2)
        

        # Calculate emission rate from rate window. t2 is proportional to t1. Beta is the proportional factor.
        en = utilities.calculate_en(t1, t2 = configuration['beta']*t1)
        # Calculate picts signal for each rate window 
        #PICTS signal = i(t1) - i(t2) but signal are very noisy, so i do an average
        i_t1 = transient_norm.iloc[t1-configuration['t_avg']:t1+configuration['t_avg']].mean()
        i_t2 = transient_norm.iloc[t2-configuration['t_avg']:t2+configuration['t_avg']].mean()
        picts = pd.concat([i_t1 - i_t2  for t1,t2 in zip(t1_index,t2_index)], axis=1)
        
        #I put in order index and columns
        picts.index=picts.index.astype(float)
        picts.columns = en.round(3)
        picts.columns.name = 'Rate Window (Hz)'
        #I put all the (t1,t2) pairs in a numpy list. I will need them later for the animation
        gates = np.array([t1, t2]).T       # I traspose it so that each row corresponds to a (t1,t2) pair. it's just for my convenience

        
        return  picts, gates


""" if __name__ == "__main__":
    
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
    #plt.show() """

   

# TODO risistemare InputHandler che gestisca anche altri tipi di input. Separare preprocessamento dei dati in un' altra classe