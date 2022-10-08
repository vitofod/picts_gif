import argparse
from enum import Enum
from pathlib import Path
import matplotlib.pyplot as plt
from picts_gif.input_handler import InputHandler
from picts_gif.picts_spectrum_plot import PictsSpectrumPlot
from picts_gif.picts_transient_plot import PictsTransientPlot

#The main.py manages the user interface through a Command Line Interface (CLI)

class PlotConfig(Enum):
    '''
    This simple enum class handles the options callable by the CLI
    
    ......................................
    Attributes
    ......................................
    transient: is selected, transient animation starts
    
    spectrum: if selected, PICTS spectrum animation starts
    
    all: if selected, both above animation start
    '''
    transient = 'transient'
    spectrum = 'spectrum'
    all = 'all'

    def __str__(self):
        return self.value

def main(): 
    '''
   This is the main methods. From here i manage input data from CLI. 
    '''
    parser = argparse.ArgumentParser()
    
    #I describe the first, the others are created with the same logic
    #data input path
    parser.add_argument(
        "-p",            #shortcut input parameter
        "--path",        #extended input parameter
        type=str, 
        required=True,   #mandatory
        help="The path to the tdms file. \n E.g.: --path /home/user/desktop/data.tdms" #the --help
        )
    
    #dictionary input path
    parser.add_argument(
        "-d", 
        "--dict", 
        type=str, 
        required=True, 
        help="The path to the dictionary json file. \n E.g.: --dict /home/user/desktop/dict.json"
        ) 
    
    #input plot options
    parser.add_argument(
        "-pl", 
        "--plot", 
        type=PlotConfig, 
        required=False,           #I am not required to view animations. I can also automatically save them to a file and only watch them later
        default=PlotConfig.all,   #If not specified, both transient and spectrum animation is performed
        choices=list(PlotConfig),
        help="Specify what to animate. \n E.g.: --plot transient -> for the transient plot. \n E.g.: --plot spectrum -> for the spectrtum plot. E.g. : --plot all -> for plot both"
        )
    
    #input plot options
    parser.add_argument(
        "-i", 
        "--interval", 
        type=float, 
        required=False,           
        default=1.,                 
        help='''The interval defines the speed of the animation. It is the time, 
                expressed in milliseconds, between one frame and another. \n
                Animations already have a default value of 1 ms \n
                E.g.: --interval 1 -> you have set the interval between one frame and another to one millisecond
                '''
        )
    
    #If you want to save you must always specify the output directory
    parser.add_argument(
        "-o", 
        "--output-dir", 
        type=str, 
        required=False, 
        default=None, 
        help="The output directory where the gif is stored. If you do not enter an output directory, the animation will not be saved"
        ) 
    
    #to show the animation
    parser.add_argument(
        '--show', 
        action='store_true', 
        help= "To show the animation digit: --show"
        )
    
    #to not show the animation
    parser.add_argument(
        '--no-show', 
        dest='show', 
        action='store_false', 
        help= "If you don't want to see the animation digit: --no-show"
        )
    
    #by default the animation is not shown
    parser.set_defaults(show=False)
   
    
    args = parser.parse_args()

    #I manage the inputs
    data = InputHandler.read_transients_from_tdms(args.path, args.dict)
    normalized_transient = InputHandler.normalized_transient(data, args.dict)
    picts, gates = InputHandler.from_transient_to_PICTS_spectrum(normalized_transient, args.dict)

   
    plots = []

    #I have to handle different types of inputs. 
    #I might want to start the transient animation only, or the PICTS spectrum animation, 
    #or both at the same time. These are three simple cases that I have implemented.
    interval = float(args.interval)
    if args.plot == PlotConfig.transient:
        fig, ax = plt.subplots(1,1, figsize=(5,5))
        plots.append( 
            PictsTransientPlot(fig, ax=ax, conf_file_path=args.dict, transient_df=normalized_transient, gates_list=gates, interval= interval)
        )

    elif args.plot == PlotConfig.spectrum:
        fig, ax = plt.subplots(1,1, figsize=(5,5))
        plots.append( 
            PictsSpectrumPlot(fig, ax=ax, df=picts, interval=interval)
        )
    elif args.plot == PlotConfig.all:
        fig, ax = plt.subplots(1,2, figsize=(10,4))
        plots += [
            PictsSpectrumPlot(fig, ax=ax[0], df=picts, interval=interval),
            PictsTransientPlot(fig, ax=ax[1], conf_file_path=args.dict, transient_df=normalized_transient, gates_list=gates, interval=interval)
        ]

    #By default I don't show the animation but I just save it.
    if args.show:
        plt.show()
    #The destination to save the output must be entered
    elif args.output_dir is None:
            print("No animations will be saved.")
    #Save the plot. I manage the creation of the destination folder
    else:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for plot in plots:
            plot.save(output_dir)

    plt.close()

#starting point
if __name__ == "__main__":
    main()