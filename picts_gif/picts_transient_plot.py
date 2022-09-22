import re
import numpy as np
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

from picts_gif.input_handler import InputHandler
from picts_gif import preprocessing

class PictsTransientPlot:


    def __init__(self, fig, ax, transient_df, gates_list, interval = 0.01): #interval = delay between frames in ms
        self.ax = ax
        self.func_anim = FuncAnimation(fig, self.ani_update, init_func=self.ani_init , interval=interval, repeat=True, frames=len(transient_df.columns)-1)
        self.transient_df = transient_df
        self.gates_list = gates_list
        self.gate_index = -1

        self.column_index = 0   #verrà incrementato ogni volta che plottiamo una curva
        self.current_column = self.transient_df.columns[self.column_index]   # tiene conto della colonna in cui ci troviamo

        self.lines = []
        self.lines += self.ax.plot([], [], label = f"Temperature: {self.transient_df.columns[self.column_index]}")
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.scatter = None  
      #TODO calcolare tutti gli indici nell'init
 
    def ani_init(self): 
        # get max of df
        self.ax.set_xlim(-0.01, 0.01)
        self.ax.set_ylim(-0.05, 1)
        self.column_index = 0 

        self.gate_index += 1
        gate = self.gates_list[self.gate_index]
        print("Current gate:", gate, "self.gate_index", self.gate_index)

        self.current_column = self.transient_df.columns[self.column_index]
        self.ax.axvline(x = gate[0], label = f't1 - {round(gate[0], 2)}', color=self.colors[self.gate_index], linestyle="dashed")
        self.ax.axvline(x = gate[1], label = f't2 - {round(gate[1], 2)}', color=self.colors[self.gate_index], linestyle="dashed")
        
        
        

        column_name = self.transient_df.columns[self.column_index]

      

        """
       .iloc[] is primarily integer position based (from 0 to length-1 of the axis), but may also be used with a boolean array.
            Allowed inputs are:
            An integer, e.g. 5.
            A list or array of integers, e.g. [4, 3, 0].
            A slice object with ints, e.g. 1:7.
            A boolean array. 
        """
        
        #ax.scatter(x= gate[0], y=self.transient_df[self.current_column].iloc[self.t1_loc[self.gate_index]])
        #ax.scatter(x= gate[1], y=self.transient_df[self.current_column].iloc[self.t2_loc[self.gate_index]])

        #ax.scatter(x= gate[0], y= 0.02)
        #ax.scatter(x= gate[1], y=0.02)


        #self.ax.legend()

        return self.lines

    def ani_update(self, frame):
      #  print(f"frame: {frame} - current_column: {self.current_column}")

        self.ax.set_title(f"Temperature: {self.current_column} K")

        # curva = colonna

        # self.lines = [colonna 1, colonna 2, ..., colonna 3]       
        # Ad ogni frame si accede all'interno della lista self.lines all'oggetto corrispondente e si chiama su quell'oggetto il metodo set_data 
        # settando i dati corrispondenti alla colonna giusta.

        # Possiamo usare i seguenti attributi di classe: self.transient_df, self.column_index, self.current_column

        # estraggo i dati che voglio plottare (aggiungo un punto in più ogni volta)
        column_data_y = self.transient_df[self.current_column]
        column_data_x = self.transient_df.index
   
        self.lines[0].set_data(column_data_x, column_data_y)

        # handle scatter points
        gate = self.gates_list[self.gate_index] # x1 e x2, corrispondono al gate i-esimo, che non cambia per tutta la durata dell'animazione
        indexes = transient.index.get_indexer(gate, method = 'backfill') # si accede ai corrispondenti indici della colonna Time
        ys = column_data_y.iloc[indexes] # si usano questi due indici, per accede ai due valori corrispenti nella colonna column_data_y (che cambia ad ogni frame)

        if self.scatter is not None:
          self.scatter.remove()
        self.scatter = self.ax.scatter(x=gate, y=ys)

        # Arrow annotation
        self.ax.annotate( 
            text=".", 
            xy = (0,0.02),
            xytext = (0,0.02),
            arrowprops=dict(arrowstyle='<->', color = 'red', linewidth=2)
            )

        #self.point_index += 1
        #self.lines[0].set_data(self.xdata[0:frame], self.ydata[0:frame])
        #ax.set_xlim(0, frame/10)
        self.column_index += 1
        self.current_column =  self.transient_df.columns[self.column_index]
        return self.lines
            

if __name__ == "__main__":
    
    data = InputHandler.read_transients_from_tdms("/home/vito/picts_gif/tests/test_data/data.tdms")
    transient, picts, gates = InputHandler.from_transient_to_PICTS_spectrum(data, "/home/vito/picts_gif/tests/test_data/dictionary.json")
    print(transient.shape)
    print(transient.iloc[463:470, :])
    #print(transient.iloc[0:1])

    fig, ax = plt.subplots(1,1)
    hp = PictsTransientPlot(fig=fig, ax=ax, transient_df=transient, gates_list=gates)
    plt.show()

    #print(gates)
    #y_index = transient.columns.get_indexer([temp], method = 'backfill')[0] for temp in transient.columns[0]])
    #print(indexes)

    #TODO sistemare l'errore IndexError: index 499 is out of bounds for axis 0 with size 499