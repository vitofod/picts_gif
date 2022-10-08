import pytest
from os.path import dirname, join
from picts_gif import input_handler 
import pandas as pd


class TestInputHandler:

    # Test if the file is read properly
    def test_read_transient_from_tdms(self):
        """ 
        This test tests that the file is read correctly and returns a dataframe
    
        GIVEN: 
            a valid input file with the correct extension
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method returns dataframe
        """
        # I get in the relative path of the file, regardless of where the project is installed 
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        
        df = input_handler.read_transients_from_tdms(test_file_path, dic_path, 'Measured Data')
        assert isinstance(df, pd.DataFrame)
        


    def test_read_transient_from_tdms_invalid_data_group_name(self):
        """ 
        This test tests that if the data_group_name in read_transient_from_tdms
        is not valid, method have to throw a KeyError
    
        GIVEN: 
            a valid input file with uncorrect data_group_name
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method has to throw an KeyError
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        #if it does not throw an exception these two lines cause the test to fail
        with pytest.raises(KeyError):
            input_handler.read_transients_from_tdms(test_file_path,dic_path, 'invalid_data_group_name')
        
    
    def test_read_transient_from_tdms_invalid_format(self):
        """ 
        This test tests that if the file have uncorrect extension, method have to throw
        exception
    
        GIVEN: 
            a bad input file 
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method has to throw exception
        """
        test_file_path = join(dirname(__file__), 'test_data/invalid_format.txt')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')

        with pytest.raises(Exception):
            input_handler.read_transients_from_tdms(test_file_path, dic_path, 'Measured Data')

    
    def test_read_transient_from_pkl(self):
        """ 
        This test tests that the file .pkl is read correctly and returns a dataframe
    
        GIVEN: 
            a valid .pkl file 
        WHEN: 
            I call the method with the file as parameter
        THEN: 
            method returns a dataframe
        """
        #I get in the relative path of the file, regardless of where the project is installed the software
        test_file_path = join(dirname(__file__), 'test_data/test.pkl')

        df = input_handler.read_transients_from_pkl(test_file_path)
        assert isinstance(df, pd.DataFrame)

    def test_check_correct_index_in_dataframe_from_tdms(self):
        """ 
        This test tests that returned dataframe index from read_transient_from_tdms
         have proper name.
    
        GIVEN: 
            a valid input file  
        WHEN: 
            I call read_transient_from_tdms with the file as parameter
        THEN: 
            dataframe index is called <Time (s)>
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        df = input_handler.read_transients_from_tdms(test_file_path, dic_path, 'Measured Data')
        assert df.index.name == 'Time (s)'

    def test_check_correct_column_name_in_dataframe_from_tdms(self):
        """ 
        This test tests that returned dataframe column name from read_transient_from_tdms
         have proper name.
    
        GIVEN: 
            a valid input file  
        WHEN: 
            I call read_transient_from_tdms with the file as parameter
        THEN: 
            dataframe columns are called <Temperature (K)>
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        df = input_handler.read_transients_from_tdms(test_file_path, dic_path, 'Measured Data')
        assert df.columns.name == 'Temperature (K)'
        
    def test_normalized_transient_check_current_value(self):
        """ 
        This test tests that the method normalized_transient correctly
        throws exception if bad current value are passed as input
    
        GIVEN: 
            a dataframe to be normalized and bad data of dark current and light current 
        WHEN: 
            I call normalized_transient(...)
        THEN: 
            if bad current values are passed as input, method trows a ValueError
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dict_path = join(dirname(__file__), 'test_data/dictionary.json')
        bad_dict_path = join(dirname(__file__), 'test_data/bad_dictionary.json')
       
        
        df = input_handler.read_transients_from_tdms(test_file_path, dict_path)
        with pytest.raises(ValueError):
            input_handler.normalized_transient(df,bad_dict_path)
            
    def test_normalized_transient_return_a_normalized_transient_current(self):
        """ 
        This test tests that returned dataframe from normalized_transient is
        properly normalized
    
        GIVEN: 
            a dataframe to be normalized 
        WHEN: 
            I call normalized_transient(...)
        THEN: 
            the current transient is normalized
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dict_path = join(dirname(__file__), 'test_data/dictionary.json')
        
       
        
        df = input_handler.read_transients_from_tdms(test_file_path, dict_path)
        normalized_df = input_handler.normalized_transient(df,dict_path)        
        assert ([normalized_df[i].index.max().max() == pytest.approx(1, abs=1e-1)] for i in normalized_df.columns)

    def test_transient_dataframe_columns_and_picts_datafram__index_have_same_lenght(self):
        """ 
        This test tests that returned index lenght dataframe <transient_norm> 
        and the column lenght of <picts> dataframe from
        from_transient_to_PICTS_spectrum have the same lenght.
    
        GIVEN: 
            the returned dataframe from read_transient_from_tdms and the proper 
            json file path with transient parameter  
        WHEN: 
            I call from_transient_to_PICTS_spectrum 
        THEN: 
            the index lenght of <transient> == column lenght of <picts>
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        df = input_handler.read_transients_from_tdms(test_file_path, dic_path, 'Measured Data')
        picts, gates = input_handler.from_transient_to_PICTS_spectrum(df,  dic_path)
        assert len(df.columns) == len(picts.index)
        
        


   