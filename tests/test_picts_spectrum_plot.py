import pytest
import matplotlib.pyplot as plt
from os.path import dirname, join
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
import numpy as np
import pandas as pd
from picts_gif import utilities
  
  


class TestSpectrumPlot:
    
##################################################
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
            
 
##################################################            
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

##################################################            
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
        
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
        df = utilities.set_column_and_index_name(df)
    
        pt = PictsSpectrumPlot(fig, ax, df)
        returned = pt.ani_init()
         
        assert isinstance(returned, list)

##################################################    
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
        
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
        df = utilities.set_column_and_index_name(df)
        
        pt = PictsSpectrumPlot(fig, ax, df)
        returned = pt.ani_update(frame=1)
         
        assert isinstance(returned, list)

##################################################        
    def test_in_ani_update_stop_and_return_a_list_if_it_finished_to_plot_the_spectrum(self):
        """ 
        This test tests that ani_update method stops and return a list
        when at the same time the current column is the last column of the dataframe 
        and all the index point are plotted
    
        GIVEN: 
           ani_update method
        WHEN: 
            at the same time the current column is the last column of the dataframe 
            and all the index point are plotted
        THEN: 
            an empty list have to be return 
        """
        fig, ax = plt.subplots()
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
        df = utilities.set_column_and_index_name(df)
        
        pt = PictsSpectrumPlot(fig, ax, df)
        #ai = PictsSpectrumPlot.ani_update(pt, frame=1)
        pt.current_column = pt.df.columns[-1]
        pt.point_index = pt.number_of_points_per_line
        returned = pt.ani_update(frame=1)
         
        assert bool(returned)
        
       
        
       