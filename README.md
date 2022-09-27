# Software & Computing project: picts_gif

## What is picts_gif project? 
Picts_gif is a tool that allows you to create animated graphics and saved it as gif. It is a project born for my need to create animated data to be projected during the discussion of the thesis, but it was written in a modular way so as to be easily modifiable and adaptable to every need. What you need is data that can be transformed into pandas Dataframes and dictionaries with specific information about the data. In my specific case, the raw data used were collected from Photo-Induced Current Transient Spectroscopy (PICTS) measurements, a spectroscopic technique used in the study of defects in the crystal lattice of semiconductor solids. The data are nothing more than measurements of photo-induced current transients as a function of temperature.

## Prerequisites
You’ll need to know a bit of [Python](https://docs.python.org/3/tutorial/). The main libraries used in this project are Matplotlib, Pandas, Numpy and Scipy. You must have Anaconda or Miniconda installed on your sytem.

## Installation
### On Linux
Deve fare gitClone
Create anaconda virtual environment with `conda env create --file environment.yml`
```
$ conda env create --file environment.yml
```
Install the library 'picts_gif' with `pip install .`
```
$ pip install .
```
### On Windows
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
         |                            |
         |__----                      |
         |__----                      |__main.py
         |__----                      |
         |                            |
         |__picts_transient_plot.py___|

```
input_handler.py manages the input files. In my case the input files are [tdms](https://www.ni.com/it-it/support/documentation/supplemental/06/the-ni-tdms-file-format.html), an extension used by LabVIEW language. The purpose of the InputHandler class in input_handler.py is to open raw data from a certain format, preprocess them and return a dataframe (or more than one) of it. To increase code readability and versatility, the utilities.py library has been created, which contains a set of methods that perform specific tasks. At this point, animations can be created from the dataframe(s). Each animation is seen as a class of its own. In this repository you can find two plotting class that i have created, picts_spettrum_plot.py and pict_transient_plot.py, but the idea is that you can create complex animations as you like by joining as many of these classes in the main as you want. picts_spettrum_plot.py manages the animation of the PICTS spectra graphs, while picts_transient_plot.py manages the animations of the current transients as a function of temperature. The main.py file is actually the "executable" of our code. It combines all the animations created (in my case two animations) and returns the output file, a gif or a mp4.
Following the installation of the project, as explained in the previous paragraph, you will find a directory on your disk called picts_gif. The structure of the various sub-folders is as follows (I omit the directories created automatically and those ignored):
```
picts_gif_____
              |_pict_gif__(code)
              |
              |_tests_____(test_code)
                        |
                        |_test_data__(data)
```
In picts_gif you will find the codes described above, while in tests you will find, in addition to the test_data directory, the codes for testing. In test_data you will find the input files accompanied by the dictionaries. 

## API reference

### input_handler.py
input_handler.py contains the static class InputHandler that handles data input. It contains 4 methods, two of which are specific for reading raw data and two for preprocessing and cleaning the data.
```
read_transients_from_tdms(path, 
                          configuration_path, 
                          data_group_name = 'Measured Data'
                        ):
```



## Usage

## Testing
All tests were done with `pytest`. The testing files all start with the name `test_ *` and are located in `tests` directory.
You can test all the code with:
```
pytest tests -v
```
If you want to test individual test_*.py files, use the command 
```
pytest tests -v <test_filename.py>
```
If you want to test specific part of test group by name of the test function, you can use the command
```
pytest -v -k "test_name_of_the_test"
```


## Tutorial
### Current transient animation
In this tutorial we will see how to animate the trend of a transient as a function of temperature. The final animation is shown in the figure. All that is needed is the file path to the directory where the data files are contained.

### Picts spectrum animation
In this tutorial we will see how to animate a PICTS spectrum. The final animation is shown in the figure. All that is needed is the file path to the directory where the data files are contained.

### Picts spectrum and current transient animation
In this tutorial we will see how to animate a PICTS spectrum. The final animation is shown in the figure. All that is needed is the file path to the directory where the data files are contained.

## Extra
### What a PICTS experiment is: a short description to better understand the code
Photo-induced transient current spectroscopy (PICTS) is a technique for investigating deep level, crystalline defects that act as recombination centers for charge carriers, and is part of the larger family of transient spectroscopy techniques. Solar cells or radiation detectors work by converting the radiation incident on the sensitive crystal into electron-hole pairs. In the presence of a potential difference at the ends of the crystal, the pairs separate and move towards the electrodes. In the presence of deep levels, however, the charge carriers are trapped and converted in a non-radiative manner, making sure that the signal present at the ends of the device is only a fraction of that generated. Knowing the mechanisms underlying these recombination phenomena allows to increase the efficiency of the devices. The idea of ​​the PICTS technique is to fill these traps with charge carriers through a photo-induced current. By stopping the external excitation, the photoinduced current will drop sharply to dark levels, while the rate of thermal emission of charge carriers by the traps can be described as [see 'The Electrical Characterization of Semiconductors: Majority Carriers and Electron States', P. Blood, J. W. Orton, Academic Pr, 1992, cap. 7] 

$
e_{i}(T) = \gamma T^2 \sigma_{ia} exp\left (- \frac{E_{ia}}{K_bT}\right )
$

where i = n for electron and i = p for hole, $σ_{ia}$ = (g0/g1)σ∞ is the so called electron/hole apparent capture cross section, with g0 and g1 respectively empty trap energy degeneracy and occupied trap energy degeneracy; T is the temperature, $E_{ia} is the apparent trap activation energy, γ is a constant. 
At the same time it is possible to describe the transient of the current as [see Tapiero et al., Journal of Applied Physics 64, 4006 (1988)]

$
 I(t) = \alpha qV \mu \tau n_t(0) e_i e^{-e_it}
$

where q is the elementary charge, V the applied voltage, $n_t(0)$ the initial trapped carrier density, t the time, $e_i$ the thermal emission rate and μτ the so called mobility-lifetime. $\alpha$ is a geometrical parameter due to the shape of the elettrical contacts.
The PICTS spectrum spin around the concept of "rate window".  The rate windows is an
arbitrarily chosen time interval from where we go to measure the difference in the current value. Referring to Figure, the istant t = 0 coincide with the LED turned off.

![A current transient](ratewindow.png)

 Once the time instant in which the transition to thermal emission occurs has been defined in the electrical transient (we can call this instant t0), we choose two successive instants t1 > t0 and t2 > t1 and express the PICTS signal as the difference in the value of the currents in these two instants:

$
S(T; t_1, t_2) = i(t_1) - i(t_2)
$

If there was no thermal emission from the traps, the current difference between the two fixed points would simply be a constant as the decay of the transient would not be perturbed by the emptying of the traps. If a trap is present, however, we expect the thermal emission to reach a maximum at a certain temperature Tm, and therefore also the difference in the PICTS signal will be characterized by a maximum exactly at the point where the thermal emission from part of
the trap is maximum. Mathematically, we can write the maximum of
S(T ; t1, t2) as

$
 \frac{dS}{dT} = \frac{dS}{de_n}\frac{de_n}{dT} = 0
$

and by considering the equations above, the solution brings to

$
  e_n (t_1 -t_2) = \ln{\frac{1 - e_nt_2}{1 - e_nt_1}}
$

This is a transcendental equation and must be solved numerically via software analysis. Ideally, considering a semiconductor in which there is only one trap state, and chosen two time instants t1 and t2, therefore, we obtain a function S(T ; t1, t2) which will show a peak at
a certain temperature $T_m$. By imposing the derivative of S(T ; t1, t2) to zero, we obtain the transcendental equation that tells us what is the value of the thermal emission rate $e_i$ we are scanning given t1 and t2. By changing values of t1 and t2, that is, by changing rate window, we obtain a curve S′(T ; t1′, t2′) identical to the previous one but shifted, since now the value of $e_n$ and $T_m$ differ from the previous one. Therefore, by choosing a collection of values t1 and t2 it is possible to obtain a collection of values $e_i$ as a function of Tm and by plotting that in an Arrhenius form we have

$
\ln{\left({T_m}^2/e_n(T_m)\right)} = \gamma \sigma + \frac{E_a}{K_bT_m}
$

from which we can extract the values ​​of the activation energy and the capture cross section of the trap(s). 

