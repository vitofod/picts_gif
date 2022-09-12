from nptdms import TdmsFile



class InputHandler:
    '''
    This class allows the reading and manipulation of TDMS type files specific to PICTS experiments or from other input
    '''
    def __init__(self):
        pass
    
    @staticmethod
    def read_transients_from_tdms(path,  data_group_name = 'Measured Data',  set_timetrack = True):
        '''
         This method transforms a TDMS file into a data frame.
         Dataframe containing current transients with time as index and temperature as columns
  
         .....................................................

         The input parameters are:
         - path: 
        string with file path of TDMS file
         - data_group_name: 
        the string key in wich data are stored in TDMS file. 'Measured Data' by defaoult
         - dropna: 
        whether to drop all rows where there is at least one NaN. Useful for faulty dataset where there are some columns with more data than others
         - set_timetrack: 
        whether to get the timetrack from the files. In some corrupted data it is better to avoid it
    

         ......................................................
         The output file is a dataframe in wich are stored current transient in function of temperature. 
        '''

        tdms_file = TdmsFile.read(path)
         # convert the 'Measured Data' group to a dataframe with all transients
        df = tdms_file[data_group_name].as_dataframe()   

         # Temperature values
      
        df.columns = [float(temp.replace('wf_','')) for temp in df.columns]
        df.columns.name = 'Temperature (K)'

 
        # set_timetrack set the zero of the transient when led turn off
        if set_timetrack:
            df.index = tdms_file[data_group_name].channels()[0].time_track() # Take index from the first channel, it should be the same for all channels (i.e.) temperatures
        #df.index = df.index.values.round(3)
        df.index.name = 'Time (s)'
        # Set t=0 on trigger
        trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']    # LV program sves in wf_trigger_offset the time of the LED triger
        df.index-=trigger
        return df

    def read_transient_from_pkl(path):
         if '.pkl' in path: 
            return pd.read_pickle(path,'bz2')  
   

# TODO risistemare InputHandler che gestisca anche altri tipi di input. Separare preprocessamento dei dati in un' altra classe