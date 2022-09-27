import argparse
from enum import Enum
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter

from picts_gif.input_handler import InputHandler
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
from picts_gif.picts_transient_plot import PictsTransientPlot

class PlotConfig(Enum):
    transient = 'transient'
    spectrum = 'spectrum'
    all = 'all'

    def __str__(self):
        return self.value

def main(args): 
    path = args.path
    config_path = args.config

    data = InputHandler.read_transients_from_tdms(args.path, args.config)
    normalized_transient = InputHandler.normalized_transient(data, args.config)
    picts, gates = InputHandler.from_transient_to_PICTS_spectrum(normalized_transient, args.config)
    
    plots = []

    if args.plot == PlotConfig.transient:
        fig, ax = plt.subplots(1,1)
        plots.append( 
            PictsTransientPlot(fig, ax=ax, transient_df=normalized_transient, gates_list=gates)
        )

    elif args.plot == PlotConfig.spectrum:
        fig, ax = plt.subplots(1,1)
        plots.append( 
            PictsSpectrumPlot(fig, ax=ax, df=picts)
        )
    elif args.plot == PlotConfig.all:
        fig, ax = plt.subplots(1,2, figsize=(5,5))
        plots += [
            PictsSpectrumPlot(fig, ax=ax[0], df=picts),
            PictsTransientPlot(fig, ax=ax[1], transient_df=normalized_transient, gates_list=gates)
        ]

    if args.show:
        plt.show()
    
    elif args.output_dir is None:
            print("No animations will be saved.")

    else:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for plot in plots:
            plot.save(output_dir)

    plt.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, required=True, help="The path to the ...")
    parser.add_argument("-c", "--config", type=str, required=True, help="The path to the ...")
    parser.add_argument("-pl", "--plot", type=PlotConfig, required=False, default=PlotConfig.all, choices=list(PlotConfig), help="transient: for the transient plot. spectrum for the spectrtum plot, all for every plot")
    parser.add_argument("-o", "--output-dir", type=str, required=False, default=None, help="Output directory") #default è il valore di output
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--no-show', dest='show', action='store_false')
    parser.set_defaults(show=False)
    args = parser.parse_args()
    main(args)