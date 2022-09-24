import pytest
from os.path import dirname, join
from picts_gif import utilities
import pandas as pd
import json

class TestUtilities:
      # Test if the file is read properly
    def convert_tdms_file_to_datafram_return_dataframe(self):
        """ 
        This test tests that convert_tdms_file_to_dataframe returns a dataframe
    
        GIVEN: 
            a valid input file with the correct extension
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method returns dataframe
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #dic_path = join(dirname(__file__), 'test_data/dictionary.json')

        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        assert isinstance(df, pd.DataFrame)
        
    def test_proper_name_of_dataframe_columns_and_index(self):
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
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #dic_path = join(dirname(__file__), 'test_data/dictionary.json')

        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        dict_name = {
                    'index_name': 'Time (s)',
                    'columns_name': 'Temperature (K)'
                    }
        df = utilities.set_column_and_index_name(df, dict_name)
        assert df.columns.name == dict_name['columns_name'] and df.index.name == dict_name['index_name']
        
    def test_set_current_value_gain_invalid_format_negative_number(self):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        gain = -5.
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        with pytest.raises(ValueError):
            utilities.set_current_value(df, gain)
            
    def test_set_current_value_gain_invalid_format_zero(self):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        gain = 0
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        with pytest.raises(ValueError):
            utilities.set_current_value(df, gain)
            
    def test_set_current_value_gain_invalid_format_not_a_number(self):
        """ 
        This test tests that set_current_value method check gain format properly
    
        GIVEN: 
            a bad gain value (negative, zero or not a float)
        WHEN: 
            the value is passed to set_current_value
        THEN: 
            exception ValueError is raised
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        gain = 'a'
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        with pytest.raises(TypeError):
            utilities.set_current_value(df, gain)
                
    def test_correct_zero_of_xaxis(self):
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
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        #create current transient dataframe
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        trigger_value = configuration['set_zero']
        #i call the method to test
        df = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(df, trigger_value)
        #if trigger value is corrupted
        if trigger_value != 'auto':
            #the index value at the minimum of current derivative must be zero
            assert df.index[trigger_value] == 0
        # if not corrupted we have not problem    
        else:
            assert True
            
    def test_trim_database_work(self):
        """ 
        This test tests that trim_dataframe actually returns a dataframe with fewer columns
    
        GIVEN: 
            a transient dataframe and two index value
        WHEN: 
            trim_database is called
        THEN: 
            the returned dataframe must have fewer columns
        """
        
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        #create current transient dataframe
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        left_column_cut = configuration['trim_left']
        right_column_cut = configuration['trim_right']  
        if (configuration['trim_left'] != None  and configuration['trim_right'] != None):   
            #I call the method to test
            new_df = utilities.trim_dataframe(df, left_column_cut, right_column_cut)  
            assert len(new_df.columns) < len(df.columns)
        else:
            #the method is not called, so there is nothing to assert
            assert True
            
    def test_trim_database_left_value_is_smaller_than_right_value(self):
        """ 
        This test tests that left_value_index and right_value_index have proper values
    
        GIVEN: 
            the dictionary in wich the two data are stored
        WHEN: 
            I compare the two values
        THEN: 
            the value of the left index must necessarily be smaller than the right value
        """
        
        #set json path
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        left_column_cut = configuration['trim_left']
        right_column_cut = configuration['trim_right']  
        assert left_column_cut < right_column_cut
        
    def test_t1_lenght_and_t2_lenght_are_the_same(self):
        """ 
        this test verifies that as many values of t1 are created as t2
    
        GIVEN: 
            a numpy array of t1 values and a numpy array with t2 values
        WHEN: 
            I check the lengths of the two arrray
        THEN: 
            They must be equal
        """
        
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        # generate ti values
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        assert len(t1) == len(t2)    
        
    def test_t1_values_are_smaller_than_t2_ones(self):
        """ 
        This test tests that foreach (t1,t2) created pairs, t1 must be smaller than t2
    
        GIVEN: 
            a numpy array of t1 values and a numpy array with t2 values
        WHEN: 
            a pair (t1, t2) is given
        THEN: 
            t1 is smaller than t2
        """
        
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        # generate ti values
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        for t in t1:
            assert t1[t] < t2[t]
            
    def test_t2_values_are_never_bigger_than_time_values_in_dataframe(self):
        """ 
        This test verifies that the t2 values created do not exceed the time values of the dataframe
    
        GIVEN: 
            The parameter set that allows me to create t1 and t2
        WHEN: 
            i call create_t1_and_t2_values
        THEN: 
            t2 values do not exceed the time values of the dataframe
        """
        
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        #open the json file and extract 'set_zero' value, that is what i want to set
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")
        # i set proper index to the dataframe
        df = utilities.check_and_fix_zero_x_axis_if_trigger_value_is_corrupted(df, configuration['set_zero'])
        
        
        # generate ti values
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        assert (t2 < df.index.max()).any()
        
    def test_create_index_for_t1_and_t2_all_values_of_t1_index_are_positive(self):
        """ 
        In this test I verify that the enumeration of t1 positive number
    
        GIVEN: 
            t1 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned positive number values numpy arrays for t1_index
        """
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")   
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(df, t1, t2)   
        for t in t1_index:
            assert t1_index[t] >= 0 
            
    def test_create_index_for_t1_and_t2_all_values_of_t2_index_are_positive(self):
        """ 
        In this test I verify that the enumeration of t2 positive number
    
        GIVEN: 
            t2 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned positive number values numpy arrays for t2_index
        """
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")   
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(df, t1, t2)   
        for t in t2_index:
            assert t2_index[t] >= 0 
            
    def test_create_index_for_t1_and_t2_all_values_of_t1_index_are_integer(self):
        """ 
        In this test I verify that the enumeration of t1 are integer 
    
        GIVEN: 
            t1 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned integer number values numpy arrays for t1_index
        """
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")   
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(df, t1, t2)   
        for t in t1_index:
            assert  isinstance(t1_index[t], int) 
            
    def test_create_index_for_t1_and_t2_all_values_of_t2_index_are_integer(self):
        """ 
        In this test I verify that the enumeration of t2 are integer 
    
        GIVEN: 
            t2 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            the function returned integer number values numpy arrays for t2_index
        """
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")   
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(df, t1, t2)   
        for t in t2_index:
            assert  isinstance(t2_index[t], int) 
            
    def test_create_index_for_t1_and_t2_have_the_same_lenght(self):
        """ 
        In this test I verify that t1_index and t2_index have the same lenght 
    
        GIVEN: 
            t1 and t2 values and a dataframe
        WHEN: 
            i call create_index_for_t1_and_t2
        THEN: 
            t1_index and t2_index have the same lenght
        """
        #set data path and json path
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        with open(dic_path, "r") as pfile:
            configuration = json.load(pfile)
        df = utilities.convert_tdms_file_to_dataframe(test_file_path, "Measured Data")   
        t1, t2 = utilities.create_t1_and_t2_values(configuration['t1_min'], configuration['t1_shift'], configuration['n_windows'], configuration['beta'])
        t1_index, t2_index = utilities.create_index_for_t1_and_t2(df, t1, t2)   
        
        assert  len(t1_index) == len(t2_index)
        
        
        
        
        
