import pandas as pd
import numpy as np
from picts_gif import utilities
import json



    
def read_transients_from_tdms(
      path : str, 
      configuration_path : str, 
      data_group_name : str = 'Measured Data' 
   ) -> pd.DataFrame :
      '''
      This method transforms a TDMS file in a Dataframe.
      The dataframe contains current transients with time as index and temperature as columns.
      .....................................................   
      .....................................................

         INPUT:
         - path: str
            string with file path of TDMS file
         - configuration_path: str
            path to a json file with all needed information to analyze the input data.
         - data_group_name: str
            the string key in wich data are stored in TDMS file. 'Measured Data' by defaoult
        
         ......................................................
         RETURN:
         - a dataframe in wich are stored current transient in function of temperature. 
         ......................................................
         ......................................................
        '''
      
      with open(configuration_path, "r") as pfile:
         configuration = json.load(pfile)
         
      # Import the file with the Tdms libraries
      # Within the tdms_file object, the acquired data is found in 'Measured Data'.
      # This option is not universal, but specific to our data acquisition system.
      #Becouse a problem in data acquisition software (LabVIEW) the data transient stored are inverted 
      #To have the proper data, i have to return the inverted dataframe
      data = -utilities.convert_tdms_file_to_dataframe(path, data_group_name)
      
      
      data = utilities.set_column_and_index_name(data)
      
      # set the correct value of the current. Transient current values come out from current amplifier. So, to have 
      # proper values of current i need to take in account the gain of current amplifier
      data = utilities.set_current_value(data, configuration['gain'])
        
      #Set the zero in x-axis. Dataframe represent current transient in function of time and temperature. Dataframe index are time values,
      #I want to set the value zero of my index exactly when current drop down. See README.md -> EXTRA for more information
      data = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(data, configuration['set_zero'])
      
      #Some trim of data. Data at low temperature are too noisy. I want to drop them. 
      #The temperature is controlled during the experiment, through a linear thermal ramp.
      #When it reaches the final temperature, it may happen that before the acquisition software stops,
      #the temperature fluctuates around the final value. This oscillation is a problem, 
      #because the temperature is the index of my columns, and it must be a monotone value. 
      if (
         configuration['trim_left'] != None  #left column index trim value
         and 
         configuration['trim_right'] != None #right column index trim value
         ):
            left_index_cut = configuration['trim_left']
            right_index_cut = configuration['trim_right']
            data = utilities.trim_dataframe(data, left_index_cut, right_index_cut)
       
      return data 

###############################################################################################################################################################
###############################################################################################################################################################


def read_transients_from_pkl(path : str) -> pd.DataFrame : 
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
        
         return pd.read_pickle(path,'bz2') 
         
###############################################################################################################################################################
###############################################################################################################################################################
           

def normalized_transient(
       transient : pd.DataFrame, 
       configuration_path : str
       ) -> pd.DataFrame :
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
         Raises
         - ValueError
            If the calculated i_light value is smaller than i_dark ones.
         ......................................................
         ......................................................
        '''
        #Transient normalization is a necessary practice to obtain a good PICTS spectrum. The spectrum 
        #could also be obtained without normalization (the physical parameters do not change) but the aspect 
        #of the spectrum would be more dispersive and more difficult to analyze and visualize.
        
       
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
       
        #To normalize the transients in order to have the value of the current equal to zero in the moments of darkness 
        # and equal to one in the moments of light, I need to know the values ​​of the dark current and the light current. 
        #The signal is noisy, so it's best to average over a given range
        
        #recover the values ​​of the dark current and light current from dictionary
        i_dark_range = [configuration['i_dark_left'], configuration['i_dark_right']]
        i_light_range = [configuration['i_light_left'], configuration['i_light_right'] ]

        #the value of the light and dark currents are the averages of the values ​​of the currents in the assigned ranges
        i_light = transient.loc[i_light_range[0]:i_light_range[1]].mean()
        i_dark = transient.loc[i_dark_range[0]:i_dark_range[1]].mean()

        #check if light current and dark current have proper values.        
        if (i_light <= i_dark).any(): raise ValueError('In normalized_transient: i_light smaller than i_dark.')
        
        transient_norm = (transient-i_dark)/(i_light-i_dark)  #normalizing in this way allows you to set the dark current to zero and the light current to one
       
        return transient_norm
     
###############################################################################################################################################################
###############################################################################################################################################################

   
def from_transient_to_PICTS_spectrum (
       transient_norm : pd.DataFrame, 
       configuration_path : str
       ):
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
            a numpy array with a collection of pair float. Each pair represent a rate window
         ......................................................
         REFERENCES:
         For a better understanding of what a PICTS spectrum is and what a rate window represents see:
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 57
          - J C Balland et al 1986 J. Phys. D: Appl. Phys. 19 71  
          - Pecunia et al. 2021, Adv. Energy Mater. 2021, 11, 2003968 with emphasis on Supporting Info
          
          You can find a short explanation in the EXTRAS in README.md on my GitHub
         ......................................................
         ......................................................
        '''
        
        
    
        with open(configuration_path, "r") as pfile:
            configuration = json.load(pfile)
        
        
        #To have a PICTS spectrum, it is necessary to evaluate the difference of the current values ​​of the transients in two successive instants t1 and t2. 
        #Each pair generates a curve of the PICTS spectrum. The spectrum is a collection of these curves.
        #I calculate the values ​​of t1 and t2
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        
        
        #Index of t1 and t2 values. Needed for using iloc later, since iloc has problems with tolerance.
        #This method allows you to enumerate the values ​​of the indexes (which are floats with many digits after the comma).
        #In this way, the first index corresponds to 1, the second to 2, etc., etc.
        #This allows me to have a one-to-one correspondence between the values ​​of t1 and t2 
        #and the indices of the time values ​​of the dataframe, which otherwise I would not know
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(transient_norm, t1, t2)
        

        # Now I calculate emission rate from rate windows
        en = utilities.calculate_en(t1, t2 = configuration['beta']*t1)
        # Calculate picts signal for each rate window 
        picts = pd.concat(
           [transient_norm.iloc[t1-configuration['t_avg']:t1+configuration['t_avg']].mean()     #current value at istant t1
           - transient_norm.iloc[t2-configuration['t_avg']:t2+configuration['t_avg']].mean() #current value at istant t2 \  
               for t1,t2 in zip(t1_index,t2_index)], # i do it for every t1 and t2 pair
            axis=1 
            )
        
        #I put in order index and columns
        picts.index=picts.index.astype(float) # more convinient for data analysis
        picts.columns = pd.Index(en.round(3))           # there is nothing special in the number 3
        picts.columns.name = 'Rate Window (Hz)'
        gates = np.array([t1, t2]).T       # I traspose it so that each row corresponds to a rate window. In fact rate window coincide with (t1 - t2)^{-1}

        
        return  picts, gates

