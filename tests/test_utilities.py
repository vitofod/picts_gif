import pytest
from os.path import dirname, join
from picts_gif import utilities
import pandas as pd
import json


##################################################
##################################################

 #return dictionary file path
@pytest.fixture
def configuration_path():
    return join(dirname(__file__), 'test_data/dictionary.json')

#return tdms file path
@pytest.fixture
def test_file_path():
    return join(dirname(__file__), 'test_data/data.tdms')

#return the dictionary
@pytest.fixture
def configuration(configuration_path):
    with open(configuration_path, "r") as pfile:
        return json.load(pfile)

#return a dataframe 7700rows x 355 columns
@pytest.fixture
def input_dataframe(test_file_path):
    #path = join(dirname(__file__), 'test_data/data.tdms')
    df = utilities.convert_tdms_file_to_dataframe(test_file_path, 'Measured Data')
    return df

##################################################
##################################################

class TestUtilities:
    
##################################################
      # Test if the file is read properly
    def test_convert_tdms_file_to_datafram_return_dataframe(self, test_file_path):
        """ 
        This test tests that convert_tdms_file_to_dataframe returns a dataframe
    
        GIVEN: 
            a valid input file with the correct extension
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method returns dataframe
        """
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        assert isinstance(df, pd.DataFrame)
    
##################################################    
    def test_convert_tdms_file_to_datafram_return_dataframe_with_7700_rows(self, test_file_path):
        """ 
        This test tests that returned dataframe from data.tdms have 7700 rows
    
        GIVEN: 
            the data.tdms input file 
        WHEN: 
            I call the method convert_tdms_file_to_dataframe with the file as parameter
        THEN: 
            method returns dataframe with 7700 rows
        """
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        df_rows = df.shape
        assert    df_rows[0] == 7700
        
##################################################    
    def test_convert_tdms_file_to_datafram_return_dataframe_with_360_columns(self, test_file_path):
        """ 
        This test tests that returned dataframe from data.tdms have 360 columns
    
        GIVEN: 
            the data.tdms input file 
        WHEN: 
            I call the method convert_tdms_file_to_dataframe with the file as parameter
        THEN: 
            method returns dataframe with 355 columns
        """
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        df_cols = df.shape
        assert    df_cols[1] == 360
    
##################################################    
    def test_proper_name_of_dataframe_columns(self, input_dataframe):
        """ 
        This test tests that transient dataframe columns have proper name
    
        GIVEN: 
            transient dataframe
        WHEN: 
            the method set_column_and_index_name are called
        THEN: 
            method returns dataframe with proper columns name 
        """
        
        
        df = utilities.set_column_and_index_name(input_dataframe)
        assert (df.columns.name == 'Temperature (K)')
     
##################################################   
    def test_proper_name_of_dataframe_index(self, input_dataframe):
        """ 
        This test tests that transient dataframe index have proper name
    
        GIVEN: 
            transient dataframe
        WHEN: 
            the method set_column_and_index_name are called
        THEN: 
            method returns dataframe with proper index name
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        
        df = utilities.set_column_and_index_name(input_dataframe)
        assert (df.index.name == 'Time (s)')    
        
##################################################    
    def test_set_current_value_gain_invalid_format_negative_number(self, input_dataframe):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        gain = -5.
        with pytest.raises(ValueError):
            utilities.set_current_value(input_dataframe, gain)
 
##################################################           
    def test_set_current_value_gain_invalid_format_zero(self, input_dataframe):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        gain = 0
        with pytest.raises(ValueError):
            utilities.set_current_value(input_dataframe, gain)
            
##################################################
    def test_set_current_value_gain_invalid_format_not_a_number(self, input_dataframe):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        gain = 'a'
        with pytest.raises(TypeError):
            utilities.set_current_value(input_dataframe, gain)
            
##################################################
    def test_set_current_value_gain_set_correct_current_value(self, input_dataframe):
        """ 
        This test tests that set_current_value method set proper current values if gain = 1e8 is passed. 
        The max current value in data.tdms is 6.91070556640625e-11
    
        GIVEN: 
            data.tdms and gain = 1e8
        WHEN: 
            i call set_current_value
        THEN: 
            maximum current value have to be 6.91070556640625e-11
        """
        gain = 1e8
        df = utilities.set_current_value(input_dataframe, gain)
        assert df.max().max() == 6.91070556640625e-11
                
##################################################
    def test_correct_zero_of_xaxis(self, input_dataframe, configuration):
        """ 
        The index of transient dataframe are time values (data are current values as a function of time).
        I want that zero of the index coincide with current drop. LabVIEW should do this automatically, 
        but sometimes (due to a bug) it doesn't, and needs to be setted up.
        This test tests that check_and_fix_zero_x_axis_if_trigger_value_is_corrupted
        set proper zero index istant.
    
        GIVEN: 
            a transient dataframe and a trigger value
        WHEN: 
            check_and_fix_zero_x_axis_if_trigger_value_is_corrupted is called
        THEN: 
            the zero of the transient dataframe index have to coincide with the minimum of the 
            current transient derivative
        """
        trigger_value = configuration['set_zero']
        #i call the method to test
        df = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(input_dataframe, trigger_value)
        assert df.index[trigger_value] == pytest.approx(0, abs=1e-3)
        
            
##################################################
    def test_trim_database_work(self, input_dataframe, configuration):
        """ 
        This test tests that trim_dataframe actually returns a dataframe with 217 columns
    
        GIVEN: 
            data.tdms dataframe and its dictionary
        WHEN: 
            trim_database is called
        THEN: 
            the returned dataframe must have 217 columns
        """
            
        left_column_cut = configuration['trim_left']
        right_column_cut = configuration['trim_right']  
        df = utilities.set_column_and_index_name(input_dataframe)
        new_df = utilities.trim_dataframe(df, left_column_cut, right_column_cut) 
        assert len(new_df.columns) == 217

##################################################
    def test_Value_Error_is_raise_if_trim_database_left_value_is_bigger_than_right_value(self, input_dataframe, configuration):
        """ 
        This test testsif a ValueError is raised if left_value_index and right_value_index are inverted
    
        GIVEN: 
            the dictionary in wich the two data are stored
        WHEN: 
            I pass these two value inverted
        THEN: 
            a ValueError is raised
        """
        
        left_cut = configuration['trim_left']
        right_cut = configuration['trim_right']  
        df = utilities.set_column_and_index_name(input_dataframe)
        
        with pytest.raises(ValueError):
            utilities.trim_dataframe(df, right_cut, left_cut)
        
##################################################
    def test_t1_and_t2_have_the_same_lenght(self,  configuration):
        """ 
        this test verifies that as many values of t1 are created as t2
    
        GIVEN: 
            a numpy array of t1 values and a numpy array with t2 values
        WHEN: 
            I check the lengths of the two arrray
        THEN: 
            They must be equal
        """
        
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        assert len(t1) == len(t2)   
        
##################################################
    def test_t1_values_are_increasing_monotone(self):
        """ 
        This test tests that t1 values are increasing monotone 
    
        GIVEN: 
            an arbitrary value for the starting point to calculate t1 
        WHEN: 
            i call the method create_t1_and_t2_values 
        THEN: 
            t1[i] < t1[i+1]
        """
        t1_min = 1
        t1_shift = 0.1
        n_windows = 5
        beta = 3
        t1, _ = utilities.create_t1_and_t2_values(t1_min, t1_shift, n_windows, beta)
        
        assert(t1[i] < t1[i+1] for i in range(0, len(t1)-1))
        
##################################################
    def test_t2_values_are_increasing_monotone(self):
        """ 
        This test tests that t2 values are increasing monotone 
    
        GIVEN: 
            an arbitrary value for the starting point to calculate t2 
        WHEN: 
            i call the method create_t1_and_t2_values 
        THEN: 
            t2[i] < t2[i+1]
        """
        t1_min = 1
        t1_shift = 0.1
        n_windows = 5
        beta = 3
        _, t2 = utilities.create_t1_and_t2_values(t1_min, t1_shift, n_windows, beta)
        
        assert(t2[i] < t2[i+1] for i in range(0, len(t2)-1))


##################################################
    def test_create_index_for_t1_and_t2_all_values_of_t1_index_are_positive(self, input_dataframe, configuration):
        """ 
        In this test I verify that the enumeration of t1 positive number
    
        GIVEN: 
            t1 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned positive number values numpy arrays for t1_index
        """
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, _ = utilities.create_index_for_t1_and_t2(input_dataframe, t1, t2)   
        
        assert (t1_index >= 0).all()         
        
##################################################
    def test_t1_values_are_smaller_than_t2_ones(self, configuration):
        """ 
        This test tests that foreach (t1,t2) created pairs, t1 must be smaller than t2
    
        GIVEN: 
            a numpy array of t1 values and a numpy array with t2 values
        WHEN: 
            a pair (t1, t2) is given
        THEN: 
            t1 is smaller than t2
        """
        
        # generate ti values
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        #for t in t1:
        assert (t1 < t2).all()
        
        
            
##################################################
    def test_t2_values_are_never_bigger_than_time_values_in_dataframe(self, input_dataframe, configuration):
        """ 
        This test verifies that the t2 values created do not exceed the time values of the dataframe
    
        GIVEN: 
            The parameter set that allows me to create t1 and t2
        WHEN: 
            i call create_t1_and_t2_values
        THEN: 
            t2 values do not exceed the time values of the dataframe
        """
        
        _, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        assert (t2 < input_dataframe.index.max()).all()
        
            
##################################################            
    def test_create_index_for_t1_and_t2_have_the_same_lenght(self, input_dataframe, configuration):
        """ 
        In this test I verify that t1_index and t2_index have the same lenght 
    
        GIVEN: 
            t1 and t2 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            t1_index and t2_index have the same lenght
        """
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(input_dataframe, t1, t2)   
        
        assert  len(t1_index) == len(t2_index)
        
##################################################
    def test_en_must_be_always_bigger_than_zero(self, configuration):
        """ 
        In this test I verify that en is always a positive number 
    
        GIVEN: 
            t1 and t2 values 
        WHEN: 
            i call calculate_en
        THEN: 
            e_n always bigger than zero
        """
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        en = utilities.calculate_en(t1, t2)
        assert (en > 0).all() 
        
        
        
        
        
