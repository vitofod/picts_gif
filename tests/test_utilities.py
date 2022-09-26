import pytest
from os.path import dirname, join
from picts_gif import utilities
import pandas as pd
import json
from picts_gif.input_handler import InputHandler


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

#return a dataframe
@pytest.fixture
def input_dataframe(configuration_path):
    path = join(dirname(__file__), 'test_data/data.tdms')
    df = InputHandler.read_transients_from_tdms(path, configuration_path, 'Measured Data')
    return df

class TestUtilities:
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
        
    def test_proper_name_of_dataframe_columns_and_index(self, input_dataframe, configuration):
        """ 
        This test tests that transient dataframe columns and index have proper names
    
        GIVEN: 
            transient dataframe
        WHEN: 
            the method set_column_and_index_name are called
        THEN: 
            method returns dataframe with proper columns name and index name
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        
        df = utilities.set_column_and_index_name(input_dataframe, configuration)
        assert df.columns.name == 'Temperature (K)' and df.index.name == 'Time (s)'
        
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
                
    def test_correct_zero_of_xaxis(self, input_dataframe, configuration):
        """ 
        The index of transient dataframe are time values (data are current values as a function of time).
        I want that zero of the index coincide with current drop. LabVIEW should do this automatically, 
        but sometimes (due to a bug) it doesn't, and needs to be setted up.
        This test tests that check_and_fix_zero_x_axis_if_trigger_value_is_corrupted
        set proper zero index istant
    
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
        #if trigger value is corrupted
        if trigger_value != 'auto':
            #the index value at the minimum of current derivative must be zero
            assert df.index[trigger_value] == pytest.approx(0, abs=1e-3)
        
            
    def test_trim_database_work(self, input_dataframe, configuration):
        """ 
        This test tests that trim_dataframe actually returns a dataframe with fewer rows
    
        GIVEN: 
            a transient dataframe and two index value
        WHEN: 
            trim_database is called
        THEN: 
            the returned dataframe must have fewer columns
        """
            
        left_column_cut = configuration['trim_left']
        right_column_cut = configuration['trim_right']  
        
        if (configuration['trim_left'] != None and configuration['trim_right'] != None):   
            #I call the method to test
            new_df = utilities.trim_dataframe(input_dataframe, left_column_cut, right_column_cut) 
            
            assert len(new_df.index) < len(input_dataframe.index)

    def test_trim_database_left_value_is_smaller_than_right_value(self, input_dataframe, configuration):
        """ 
        This test tests that left_value_index and right_value_index have proper values
    
        GIVEN: 
            the dictionary in wich the two data are stored
        WHEN: 
            I compare the two values
        THEN: 
            the value of the left index must necessarily be smaller than the right value
        """
        
        left_cut = configuration['trim_left']
        right_cut = configuration['trim_right']  
        with pytest.raises(ValueError):
            utilities.trim_dataframe(input_dataframe, left_cut, right_cut)
        
    def test_t1_lenght_and_t2_lenght_are_the_same(self, input_dataframe, configuration):
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
        
    def test_t1_values_are_smaller_than_t2_ones(self, input_dataframe, configuration):
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
        for t in t1:
            assert t1[t] < t2[t]
            
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
        
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        assert (t2 < input_dataframe.index.max()).any()
        
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
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(input_dataframe, t1, t2)   
        for t in t1_index:
            assert t1_index[t] >= 0 
        #There is no need to create the same test for t2, as we have previously verified that t2 > t1
            
   
            
    def test_create_index_for_t1_and_t2_all_values_of_t1_index_are_integer(self, input_dataframe, configuration):
        """ 
        In this test I verify that the enumeration of t1 are integer 
    
        GIVEN: 
            t1 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned integer number values numpy arrays for t1_index
        """
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(input_dataframe, t1, t2)   
        for t in t1_index:
            assert  isinstance(t1_index[t], int) 
            
    def test_create_index_for_t1_and_t2_all_values_of_t1_index_are_integer(self, input_dataframe, configuration):
        """ 
        In this test I verify that the enumeration of t1 are integer 
    
        GIVEN: 
            t1 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned integer number values numpy arrays for t1_index
        """
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(input_dataframe, t1, t2)   
        for t in t2_index:
            assert  isinstance(t2_index[t], int) 
            
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
        assert (utilities.calculate_en(t1, t2)).any() > 0
        
        
        
        
        
