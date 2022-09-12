import pytest

class TestPreprocessing:
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