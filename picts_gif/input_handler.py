from nptdms import TdmsFile
import pandas as pd
import numpy as np
from picts_gif import preprocessing
import json


class InputHandler:
    '''
    This class allows the reading and manipulation of TDMS type files specific to PICTS experiments or from other input
    '''
    def __init__(self):
        pass
    
    @staticmethod
    def read_transients_from_tdms(path, data_group_name = 'Measured Data'):
        '''
         This method transforms a TDMS file into a data frame.
         The dataframe contains current transients with time as index and temperature as columns.
  
         .....................................................

         The input parameters are:
         - path: 
            string with file path of TDMS file
         - data_group_name: 
            the string key in wich data are stored in TDMS file. 'Measured Data' by defaoult
        
         ......................................................
         The output file is a dataframe in wich are stored current transient in function of temperature. 
        '''
        # Import the file with the Tdms libraries
        tdms_file = TdmsFile.read(path)
        # Within the tdms_file object, the acquired data is found in 'Measured Data'.
        # This option is not universal, but specific to our data acquisition system in Bologna.
        data = tdms_file[data_group_name].as_dataframe()   

        # I arrange the labels of the columns. The acquisition system provides a standard name of the type 'wf_ <temperature value>'. 
        # For convenience, I want the name of the columns to coincide with the value of the temperature at which the current transient was measured.
        data.columns = [float(temp.replace('wf_','')) for temp in data.columns]
        data.columns.name = 'Temperature (K)'

 
        # I want to set the index (the time, it will be my x-axis) and arrange the x-axis so that the zero of my reference system coincides 
        # with the LED turning off. 
        # The moment the LED turns off is recorded in the Tdms file, as it is used as a trigger for the acquisition of the measurement.
        # Take index from the first channel, it should be the same for all channels (i.e.) temperatures. 
        data.index = tdms_file[data_group_name].channels()[0].time_track()
        data.index.name = 'Time (s)' #Rename the index
        # LabVIEW program saves in 'wf_trigger_offset' info of the LED trigger
        trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']  
        data.index -= trigger
        return -data

    def read_transients_from_pkl(path):
         '''
         This method transforms a.pkl into a data frame.
         Dataframe containing current transients with time as index and temperature as columns
  
         .....................................................

         The input parameters are:
         - path: 
            string with file path of TDMS file
         ......................................................
         The output file is a dataframe in wich are stored current transient in function of temperature. 
        '''
         if '.pkl' in path: 
            return pd.read_pickle(path,'bz2')   



    def from_transient_to_PICTS_spectrum (data, configuration_path):
        '''
         This method transforms the raw data input from 'read_transient_from_*' into a dataframe containing the PICTS spectrum.
         Dataframe have temperature as index and rate window as columns
  
         .....................................................

         The input parameters are:
         - data: 
            dataframe to analyze 
         - parameters_path:
            path to a json file with all needed information to analyze the input data
        
         ......................................................
         The output file are:
         - transient:
             a dataframe in wich are stored processed current transient in function of temperature, with time as index and temperature as columns.
         - picts:
            a dataframe with the picts spectrum, with temperature as index and 'rate window' as columns.    
        '''
        #TODO il problema è da dove inizia a contare il tempo
        
        #open the json parameters file
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
        # set the correct value of the current. 
        #check amplifier_gain > 0
        if configuration['gain'] < 0:  raise ValueError('In set_amplifier_gain: Not appropiate value.')
        transient = data/configuration['gain']   
        #It is possible that the trigger data that sets the zero of the transient is corrupted. 
        # If the data is corrupted, set zero from the configuration file. 
        if configuration['set_zero'] != 'auto':
            value = configuration['set_zero']
            print(value)
            print(transient[value].diff().idxmin())
            transient.index -= transient[value].diff().idxmin() #the zero is positioned exactly in 
                                                                                    #the minimum of the derivative 
                                                                                    # (this is due to the shape of the signal)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1,1)
        transient.iloc[:,50:51].plot(ax=ax)
        plt.title("transient")

        #normalized the current transient
        #recover the values ​​of the dark current
        i_dark_range = [configuration['i_dark_left'], configuration['i_dark_right']]
        #recover the values ​​of the light current
        i_light_range = [configuration['i_light_left'], configuration['i_light_right'] ]
        #the value of the light and dark currents are the averages of the values ​​of the currents in the assigned ranges
        i_light = transient.loc[i_light_range[0]:i_light_range[1]].mean()
        i_dark = transient.loc[i_dark_range[0]:i_dark_range[1]].mean()
        print(i_light, i_dark)
       # if i_light.iloc[0:1] < i_dark.iloc[0:1]:  raise ValueError('In normalized_transient: i_light smaller than i_dark.')
        transient_norm = (transient-i_dark)/(i_light-i_dark)
        transient_norm.iloc[:,50:51].plot()
        plt.title("transient_norm")

        #I calculate the values ​​of t1
        t1 = preprocessing.create_t1_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'])
        
        
        # Create t2 based on t1 and beta
        t2 = np.array([configuration['beta']*t1 for t1 in t1])
        if (t2>transient_norm.index.max()).any():      # If any value in t2 is bigger than the maximum time of the transients
           raise ValueError('Some t2 values are bigger than the highest value of the transient time index. Adjust your t1 and beta accordingly.')

    
       
        # location of t1 values. needed for using iloc later since loc has problems with tolerance
        t1_loc = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t1])    
        t2_loc = np.array([transient_norm.index.get_indexer([t], method = 'backfill')[0] for t in t2])    # location of t2 vcalues
        
        # Calculate rate windows.
        en = preprocessing.calculate_en(t1, t2 = configuration['beta']*t1)
        # Calculate picts signal for each rate window 
        picts = pd.concat([transient_norm.iloc[t1-configuration['t_avg']:t1+configuration['t_avg']].mean() 
                            - transient_norm.iloc[t2-configuration['t_avg']:t2+configuration['t_avg']].mean() \
                           for t1,t2 in zip(t1_loc,t2_loc)], axis=1)
        
        #I put in order index and columns
        picts.index=picts.index.astype(float)
        picts.columns = en.round(3)
        picts.columns.name = 'Rate Window (Hz)'
        gates = np.array([t1, t2]).T       # I traspose it so that each row corresponds to a rate window

        import matplotlib.pyplot as plt
       # fig, ax = plt.subplots(1,1)
        #transient_norm.iloc[:,50:51].plot(ax=ax)
        #transient.iloc[:,50:51].plot()
        #picts.iloc[:,0:1].plot()
        plt.show()

       
        
        return transient_norm, picts, gates


if __name__ == "__main__":
    
    path = '/home/vito/picts_gif/tests/test_data/data.tdms'
    dic_path = '/home/vito/picts_gif/tests/test_data/dictionary.json'
    
    
    data = InputHandler.read_transients_from_tdms(path)
    transient, picts, gates = InputHandler.from_transient_to_PICTS_spectrum(data,  dic_path)
     
    

   

# TODO risistemare InputHandler che gestisca anche altri tipi di input. Separare preprocessamento dei dati in un' altra classe