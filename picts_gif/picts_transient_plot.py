import re
import numpy as np
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from picts_gif.input_handler import InputHandler
from picts_gif import preprocessing

class PictsTransientPlot:
    def __init__(self, ax, df, interval = 0.01): #interval = delay between frames in ms
        self.ax = ax
        self.ax.set_title(f"Temperature: -" )
        self.func_anim = FuncAnimation(fig, self.ani_update, init_func=self.ani_init , interval=interval)
        self.df = df

        self.column_index = 0   #verrà incrementato ogni volta che plottiamo una curva
        self.current_column = df.columns[self.column_index]   # tiene conto della colonna in cui ci troviamo

        self.lines = []
        self.lines += self.ax.plot([], [], label = f"Temperature: {self.df.columns[self.column_index]}")

    def ani_init(self): 
        # get max of df
        self.ax.set_xlim(self.df.index.min(), self.df.index.max())
        self.ax.set_ylim(0, 0.5e-9)
        return self.lines

    def ani_update(self, frame):
        
        # curva = colonna

        # self.lines = [colonna 1, colonna 2, ..., colonna 3]       
        # Ad ogni frame si accede all'interno della lista self.lines all'oggetto corrispondente e si chiama su quell'oggetto il metodo set_data 
        # settando i dati corrispondenti alla colonna giusta.

        # Possiamo usare i seguenti attributi di classe: self.df, self.column_index, self.current_column

        # estraggo i dati che voglio plottare (aggiungo un punto in più ogni volta)
        column_data_y = self.df[self.current_column]
        column_data_x = self.df.index
   
        self.lines[0].set_data(column_data_x, column_data_y)

        #self.point_index += 1

        print(f"frame: {frame} - current_column: {self.current_column} -  y size: {len(column_data_y)}")

        
        #self.lines[0].set_data(self.xdata[0:frame], self.ydata[0:frame])
        #ax.set_xlim(0, frame/10)
        self.column_index += 1
        self.current_column =  self.df.columns[self.column_index]
        return self.lines
            

if __name__ == "__main__":
    
    data = InputHandler.read_transients_from_tdms("/home/vito/picts_gif/tests/test_data/data.tdms")
    data = preprocessing.set_amplifier_gain(data, 1e9)
    print(data.shape)
    print(data.head())
    print(data.columns.names)
    
    #data = preprocessing.set_zero_at_trigger(data, data.columns) non serve proprio questa funzione
    
    fig, ax = plt.subplots(1,1)
    hp = PictsTransientPlot(ax=ax, df=data)
    set
    plt.show()




    #TODO sistemare l'errore IndexError: index 499 is out of bounds for axis 0 with size 499