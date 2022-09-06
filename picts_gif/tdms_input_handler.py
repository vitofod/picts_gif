from nptdms import TdmsFile



class TdmsInputHandler:
    def __init__(self):
        pass

    def read_transients (path, data_group_name = 'Measured Data', amplifier_gain=1, dropna=False, set_timetrack = True, drop=None, sep='.'):
    '''
    path: string with file path of TDMS file
    amplifier_gain: gain set on the current amplifier (to extract current from voltage values)
    current_scale: Order of magnitude of the currents to scale the data (e.g. 1e-9 sets values to nA). Set 1 to leave as measured
    time_scale: Order of magnitude of the times to scale the data (e.g. 1e-6 sets values to µA). Set 1 to leave as measured
    dropna: whether to drop all rows where there is at least one NaN. Useful for faulty dataset where there are some columns with more data than others
    set_timetrack: whether to get the timetrack from the files. In some corrupted data it is better to avoid it
    drop: list of 2 integers indicating the initial and final columns to be dropped from the dataframe as soon as it is imported. Usually used to remove the first or last columns which may contain corrupted data. If drop=[0,5] drop the first 2 columns\n
    sep: string indicating decimal separator for temperature values in case it is not the standard dot.\n
    '''

   # if '.pkl' in path: return pd.read_pickle(path,'bz2')   # If transient is passed as compressed pickle file as returned by save_transients
    tdms_file = TdmsFile.read(path)
    df = tdms_file[data_group_name].as_dataframe()    # convert the 'Measured Data' group to a dataframe with all transients

    if dropna: df=df.dropna()

   # if drop is not None: df = df.drop(axis=1, columns = df.columns[drop[0]:drop[1]]) 

    # Temperature values
    if sep != '.': df.columns = [temp.replace(sep, '.') for temp in df.columns] 
    df.columns = [float(temp.replace('wf_','')) for temp in df.columns]
    df.columns.name = 'Temperature (K)'

    # Current values
    df=df/amplifier_gain                # Convert to current

    # Time values
    if set_timetrack:
        df.index = tdms_file[data_group_name].channels()[0].time_track() # Take index from the first channel, it should be the same for all channels (i.e.) temperatures
    #df.index = df.index.values.round(3)
    df.index.name = 'Time (s)'
    # Set t=0 on trigger
    trigger = tdms_file[data_group_name].channels()[0].properties['wf_trigger_offset']    # LV program sves in wf_trigger_offset the time of the LED triger
    df.index-=trigger
    return df

