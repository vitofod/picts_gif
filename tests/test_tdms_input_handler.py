import pytest
from os.path import dirname, join
from picts_gif.tdms_input_handler import TdmsInputHandler
import pandas as pd

class TestTdmsInputHandler:

    # Il file viene letto corretteamente e non ci sono problemi
    def test_read_transient(self):
        # ottengo in il path relativo del file, indipendentemente da dove è installato il progetto il software
        test_file_path = join(dirname(__file__), 'test_data/test.tdms')

        df = TdmsInputHandler.read_transients(test_file_path, 'Measured Data', set_timetrack=True)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty


    # Si passa un data_group_name non valido e si verifica che la funzione lanci un'eccezione
    def test_read_transient_invalid_data_group_name(self):

        test_file_path = join(dirname(__file__), 'test_data/test.tdms')
        #se non lancia una eccezione queste due righe fanno fallire il test
        with pytest.raises(KeyError):
            TdmsInputHandler.read_transients(test_file_path, 'invalid_data_group_name', set_timetrack=True)
        
    
    # Verifico eccezione se file non tdms
    def test_read_transient_invalid_format(self):
        """
        FAILED tests/test_tdms_input_handler.py::TestTdmsInputHandler::test_read_transient_invalid_format - 
        KeyError: "There is no group named 'Measured Data' in the TDMS file"    
        mi passa la cosa del formato ma come il test precedente si arrabbia col Measured Data    
        """

        test_file_path = join(dirname(__file__), 'test_data/invalid_format.txt')

        # with pytest.raises(Exception):
        TdmsInputHandler.read_transients(test_file_path, 'Measured Data', set_timetrack=True)
    