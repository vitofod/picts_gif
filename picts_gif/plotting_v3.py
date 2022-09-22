
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from picts_gif.input_handler import InputHandler
from picts_gif import preprocessing
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
from picts_gif.picts_transient_plot import PictsTransientPlot

if __name__ == "__main__":

    path = '/home/vito/picts_gif/tests/test_data/data.tdms'
    dic_path = '/home/vito/picts_gif/tests/test_data/dictionary.json'
    #data = InputHandler.read_transients_from_pkl("/home/vito/picts_gif/tests/test_data/test.pkl")
    data = InputHandler.read_transients_from_tdms(path)
    transient, picts, gates = InputHandler.from_transient_to_PICTS_spectrum(data, dic_path)
    
    # print(data[819.900].iloc[0:5])
    # 1 Definire la figura e gli assi
    fig, ax = plt.subplots(1,2)
    hp = PictsSpectrumPlot(fig, ax=ax[0], df=picts)        

    data = InputHandler.read_transients_from_tdms("/home/vito/picts_gif/tests/test_data/data.tdms")
    transient, picts, gates = InputHandler.from_transient_to_PICTS_spectrum(data, "/home/vito/picts_gif/tests/test_data/dictionary.json")

    hp = PictsTransientPlot(fig, ax=ax[1], df=transient)
    plt.show()

