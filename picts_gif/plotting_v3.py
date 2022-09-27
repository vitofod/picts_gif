
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from picts_gif.input_handler import InputHandler
from picts_gif import utilities
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
from picts_gif.picts_transient_plot import PictsTransientPlot

"""
* Sistemare i tests   FATTO
* Code coverage (pytest-cov) https://pytest-cov.readthedocs.io/en/latest/ pytest --cov=myproj tests/ FATTO
* Scrivere il main con una CLI (argparse) FATTO
* Terminare l'animazione senza eccezione FATTO


* Completare il README (come si lancia il main del software)
* Provare a installare il software from scratch

* Esportare il plot in .gif / .mp4 (installare pillow oppure imagemagik)
* Testare il salvataggio del plot
* Il terzo plot (optional)
"""


if __name__ == "__main__":

    path = '/home/vito/picts_gif/tests/test_data/data.tdms'
    dic_path = '/home/vito/picts_gif/tests/test_data/dictionary.json'
    #data = InputHandler.read_transients_from_pkl("/home/vito/picts_gif/tests/test_data/test.pkl")
    data = InputHandler.read_transients_from_tdms(path, dic_path)
    normalized_transient = InputHandler.normalized_transient(data, dic_path)
    picts, gates = InputHandler.from_transient_to_PICTS_spectrum(normalized_transient, dic_path)
    
    # print(data[819.900].iloc[0:5])
    # 1 Definire la figura e gli assi
    fig, ax = plt.subplots(1,2)
    hp = PictsSpectrumPlot(fig, ax=ax[0], df=picts)        


    hp = PictsTransientPlot(fig, ax=ax[1], transient_df=normalized_transient, gates_list=gates)
    plt.show()
    

