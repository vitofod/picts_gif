from nptdms import TdmsFile



class TdmsInputHandler:
    '''
    This class allows the reading and manipulation of TDMS type files specific to PICTS experiments
    '''
    def __init__(self):
        pass

    def read_transients(path,  data_group_name = 'Measured Data',  set_timetrack = True,  sep='.'):
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
         - sep: 
        string indicating decimal separator for temperature values in case it is not the standard dot.\n

         ......................................................
         The output file is a dataframe in wich are stored current transient in function of temperature. 
        '''

        tdms_file = TdmsFile.read(path)
         # convert the 'Measured Data' group to a dataframe with all transients
        df = tdms_file[data_group_name].as_dataframe()   

         # Temperature values
        if sep != '.': df.columns = [temp.replace(sep, '.') for temp in df.columns] 
        df.columns = [float(temp.replace('wf_','')) for temp in df.columns]
        df.columns.name = 'Temperature (K)'

 
        # Time values
        if set_timetrack:
            df.index = tdms_file[data_group_name].channels()[0].time_track() # Take index from the first channel, it should be the same for all channels (i.e.) temperatures
        #df.index = df.index.values.round(3)
        df.index.name = 'Time (s)'
        # Set t=0 on trigger
        trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']    # LV program sves in wf_trigger_offset the time of the LED triger
        df.index-=trigger
        return df


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
            Usually used to remove the first or last columns which may contain corrupted data. If drop=[0,5] drop the first 2 columns\n
        '''
        if dropna: df=df.dropna()
        if drop is not None: df = df.drop(axis=1, columns = df.columns[drop[0]:drop[1]]) 
        return df

