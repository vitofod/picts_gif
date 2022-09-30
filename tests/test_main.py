
from typing import Sequence
import pytest
from picts_gif.main import PlotConfig
from enum import Enum
import argparse
from picts_gif import main
from os.path import dirname, join
from argparse import Namespace
import matplotlib.pyplot as plt


@pytest.fixture
def input_bad_path_option():
    return '-p /home/bad/path -d ' + join(dirname(__file__), 'test_data/dictionary.json') + ' --no-show'

@pytest.fixture
def main_test():
    pass

#return tdms file path
@pytest.fixture
def test_file_path():
    return join(dirname(__file__), 'test_data/data.tdms')

class TestMain:
    
    def test_PlotConfig_enum_class_value_transient(self):
        """ 
        This test tests transient value in PlotConfig
    
        GIVEN: 
            PlotConfig enum class
        WHEN: 
            I call the transient value
        THEN: 
            must be == transient
        """
        a = PlotConfig.transient.name 
        assert (a == 'transient' )
        
    def test_PlotConfig_enum_class_value_spectrum(self):
        """ 
        This test tests spectrum value in PlotConfig
    
        GIVEN: 
            PlotConfig enum class
        WHEN: 
            I call the spectrum value
        THEN: 
            must be == spectrum
        """
        b = PlotConfig.spectrum.name 
        assert (b == 'spectrum' )
        
    def test_PlotConfig_enum_class_value_all(self):
        """ 
        This test tests all value in PlotConfig
    
        GIVEN: 
            PlotConfig enum class
        WHEN: 
            I call the all value
        THEN: 
            must be == all
        """
        c = PlotConfig.all.name 
        assert (c == 'all' )
        
    def test_main_bad_data_path(self):
        """ 
        This test tests that FileNotFoundError is properly raised if a bad input tdms data path is parsed to the main
    
        GIVEN: 
            bad input tdms data path
        WHEN: 
            I call the main() method
        THEN: 
            FileNotFoundError have to be raised
        """
        dic_path = join(dirname(__file__), 'test_data/dictionary.json')
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--path", type=str, required=True)
        parser.add_argument("-d", "--dict", type=str, required=True) 
        
        args = parser.parse_args(['--path', 'home/bad/file/path','--dict', dic_path])
        with pytest.raises(FileNotFoundError):
            main.main(args)     
        
    def test_main_bad_dictionary_path(self):
        """ 
        This test tests that FileNotFoundError is properly raised if a bad input dictionary path is parsed to the main
    
        GIVEN: 
            bad input dictionary path
        WHEN: 
            I call the main() method
        THEN: 
            FileNotFoundError have to be raised
        """
        test_file_path = join(dirname(__file__), 'test_data/data.tdms')
       
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--path", type=str, required=True, help="The path to the tdms file. \n E.g.: --path /home/user/desktop/data.tdms" )
        parser.add_argument("-d", "--dict", type=str, required=True, help="The path to the dictionary json file. \n E.g.: --dict /home/user/desktop/dict.json") 
        
        args = parser.parse_args(['--path', test_file_path,'--dict', 'test2'])
        with pytest.raises(FileNotFoundError):
            main.main(args)    
            
   
        
    