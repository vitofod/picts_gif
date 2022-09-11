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
    

    #Verifico che il metodo riceva un dataframe e un intero
    def test_set_amplifier_gain_invalid_format(self):
        #è un dataframe?
        assert isinstance(df, pd.DataFrame)
        #è un numero intero positivo?
        assert type(amplifier_gain) == int, "Incorrect input, not an integer"
    

     def test_optimize_dataframe(self):
        #è un dataframe?
        assert isinstance(df, pd.DataFrame)
        #dropna è un boolean?
        assert type(dropna) == bool
        #drop è una list di integer?

    #Prima di essere settato, gli istanti temporali sono tutti positivi. Se si setta lo zero
    # del tempo alla caduta del transiente, alla sinistra i dati saranno negativi    
    def test_set_zero_at_trigger_go_well(self):
        assert df.index[0] < 0

    #il transiente normalizzato ha valori di corrente di luce compresi attorno 1, non normalizzato ~ 1e-9
    def test_normalized_transient(self):
        i_light = df.loc[i_light_range[0]:i_light_range[1]].mean()
        i_light_norm = tr_norm.loc[i_light_range[0]:i_light_range[1]].mean()
        assert i_light_norm > i_light