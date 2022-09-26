# Software & Computing project: picts_gif

## What is picts_gif project? 
Picts_gif is a tool that allows you to create animated graphics and saved it as gif. It is a project born for my need to create animated data to be projected during the discussion of the thesis, but it was written in a modular way so as to be easily modifiable and adaptable to every need. What you need is data that can be transformed into pandas Dataframes and dictionaries with specific information about the data. In my specific case, the raw data used were collected from Photo-Induced Current Transient Spectroscopy (PICTS) measurements, a spectroscopic technique used in the study of defects in the crystal lattice of semiconductor solids. The data are nothing more than measurements of photo-induced current transients as a function of temperature.

## Prerequisites
You’ll need to know a bit of [Python](https://docs.python.org/3/tutorial/). The main libraries used in this project are Matplotlib, Pandas, Numpy and Scipy.

## Installation
# On Linux
Create anaconda virtual environment with `conda env create --file environment.yml`
```
$ conda env create --file environment.yml
```
Install the library 'picts_gif' with `pip install .`
```
$ pip install .
```
# On Windows
Install any [Linux](https://help.ubuntu.com/community/DualBoot) distribution, then go back to the previous paragraph.
I don't use Windows or Mac, so I'm sorry but I can't help you more than that.


## Structure of the code
You now have everything you need on your computer. The code can be described by the following structure:
```
          ______utilities.py
         |
input_handler.py
         |
         |__picts_spectrum_plot.py____
         |                            |__main.py
         |__picts_transient_plot.py___|

```
input_handler.py manages the input files. In my case the input files are [tdms](https://www.ni.com/it-it/support/documentation/supplemental/06/the-ni-tdms-file-format.html), an extension used by LabVIEW language. The purpose of the InputHandler class is to open data from a certain format and return a dataframe of it. To increase code readability and versatility, the utilities.py library has been created which contains a set of methods that perform specific tasks. At this point, animations can be created from the dataframe(s). Each animation is seen as a class of its own. In my case picts_spettrum_plot.py manages the animation of the PICTS spectra graphs, while picts_transient_plot.py manages the animations of the current transients as a function of temperature. The main.py file is actually the "executable" of our code. It combines all the animations created (in my case two animations) returning the output file, a gif.
Following the installation of the project, as explained in the previous paragraph, you will find a directory on your disk called picts_gif. The structure of the various sub-folders is as follows:
```
picts_gif_____
              |_pict_gif_code
              |
              |_
```


## Testing

Test the library with:
`pytest tests -v`
## Usage

## Tutorial

