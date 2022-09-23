import pytest
from os.path import dirname, join
from picts_gif import utilities
import pandas as pd

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
        The dataframe transient index are time values (data are current values in function of time).
        I want to set the index at zero when current drop. LabVIEW should do this automatically, 
        but sometimes (due to a bug) it doesn't and needs to be setted up.
        This test tests that check_and_fix_trigger_value_if_corrupted set the zero with the istant of current drop
    
        GIVEN: 
            a transient dataframe and a trigger value
        WHEN: 
            check_and_fix_trigger_value_if_corrupted
        THEN: 
            the zero of the transient dataframe index have to coincide with the minimum of the 
            current transient derivative
        """
        pass
                
        
