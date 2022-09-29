import pytest
import matplotlib.pyplot as plt
from os.path import dirname, join
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
from picts_gif.input_handler import InputHandler
import numpy as np
import pandas as pd
import json
from picts_gif import utilities
  
  


class TestSpectrumPlot:
    

    def test_raise_type_error_if_df_is_not_pandas_dataframe(self):
        """ 
        This test tests whether an TypeError is thrown if I initialize an object of the PictsSpectrumPlot class by passing it a wrong dataframe argument
    
        GIVEN: 
           a bad object of the dataframe class
        WHEN: 
            I initialize an object of the PictsSpectrumPlot class
        THEN: 
            a TypeError exception is thrown
        """
        fig, ax = plt.subplots()
         
        with pytest.raises(TypeError):
            PictsSpectrumPlot.__init__(self,fig=fig, ax=ax, df='a')
            
            
    def test_raise_type_error_if_interval_is_not_float(self):
        """ 
        This test tests whether an TypeError is thrown if I initialize an object of the PictsSpectrumPlot class by passing it a wrong interval argument
    
        GIVEN: 
           a bad interval type value 
        WHEN: 
            I initialize an object of the PictsSpectrumPlot class
        THEN: 
            a TypeError exception is thrown
        """
        fig, ax = plt.subplots()
        df = pd.DataFrame()
        gate = np.array([0,1])
         
        with pytest.raises(TypeError):
            PictsSpectrumPlot.__init__(self,fig=fig, ax=ax, df=df, interval='a')
            
    def test_ani_init_return_a_list(self):
        """ 
        This test tests that ani_init method return a list
    
        GIVEN: 
           ani_init method
        WHEN: 
            I call it
        THEN: 
            a list have to be return
        """
        fig, ax = plt.subplots()
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
        df = utilities.set_column_and_index_name(df)
        picts, gate = InputHandler.from_transient_to_PICTS_spectrum(df, dic_path)
        pt = PictsSpectrumPlot(fig, ax, df)
        returned = pt.ani_init()
         
        assert isinstance(returned, list)
    
    def test_ani_update_return_a_list(self):
        """ 
        This test tests that ani_update method return a list
    
        GIVEN: 
           ani_update method
        WHEN: 
            I call it
        THEN: 
            a list have to be return
        """
        fig, ax = plt.subplots()
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
        df = utilities.set_column_and_index_name(df)
        
        pt = PictsSpectrumPlot(fig, ax, df)
        returned = pt.ani_update(frame=1)
         
        assert isinstance(returned, list)
        
       