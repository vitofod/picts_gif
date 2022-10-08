import pytest
import matplotlib.pyplot as plt
from os.path import dirname, join
from picts_gif.picts_transient_plot import PictsTransientPlot
from picts_gif import input_handler 
import numpy as np
import pandas as pd
from picts_gif import utilities
  
  


class TestTransientPlot:
    

    def test_raise_type_error_if_transient_is_not_pandas_dataframe(self):
        """ 
        This test tests whether an TypeError is thrown if I initialize an object of the PictsTransientPlot class by passing it a wrong dataframe argument
    
        GIVEN: 
           a bad object of the dataframe class
        WHEN: 
            I initialize an object of the PictsTransientPlot class
        THEN: 
            a TypeError exception is thrown
        """
        fig, ax = plt.subplots()
        gate = np.array([0,1])
         
        with pytest.raises(TypeError):
            PictsTransientPlot.__init__(self,fig=fig, ax=ax, transient_df='a', gates_list=gate)
            
    def test_raise_type_error_if_gates_list_is_not_numpy_ndarray(self):
        """ 
        This test tests whether an TypeError is thrown if I initialize an object of the PictsTransientPlot class by passing it a wrong numpy argument
    
        GIVEN: 
           a bad object of the numpy.ndarray class
        WHEN: 
            I initialize an object of the PictsTransientPlot class
        THEN: 
            a TypeError exception is thrown
        """
        fig, ax = plt.subplots()
        df = pd.DataFrame()
         
        with pytest.raises(TypeError):
            PictsTransientPlot.__init__(self,fig=fig, ax=ax, transient_df=df, gates_list='a')
            
    def test_raise_type_error_if_interval_is_not_float(self):
        """ 
        This test tests whether an TypeError is thrown if I initialize an object of the PictsTransientPlot class by passing it a wrong interval argument
    
        GIVEN: 
           a bad interval type value 
        WHEN: 
            I initialize an object of the PictsTransientPlot class
        THEN: 
            a TypeError exception is thrown
        """
        fig, ax = plt.subplots()
        df = pd.DataFrame()
        gate = np.array([0,1])
         
        with pytest.raises(TypeError):
            PictsTransientPlot.__init__(self,fig=fig, ax=ax, transient_df=df, gates_list=gate, interval='a')
            
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
        picts, gate = input_handler.from_transient_to_PICTS_spectrum(df, dic_path)
        pt = PictsTransientPlot(fig, ax, dic_path, df, gate)
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
        picts, gate = input_handler.from_transient_to_PICTS_spectrum(df, dic_path)
        pt = PictsTransientPlot(fig, ax, dic_path, df, gate)
        returned = pt.ani_update(frame=1)
         
        assert isinstance(returned, list)
        
       