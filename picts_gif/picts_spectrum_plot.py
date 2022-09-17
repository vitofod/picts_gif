import re
import numpy as np
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from picts_gif.input_handler import InputHandler

class PictsSpectrumPlot:
    def __init__(self, ax, df, interval = 0.1): #interval = delay between frames
        self.ax = ax
        self.ax.set_title("Picts Spectrum")
        self.func_anim = FuncAnimation(fig, self.ani_update, init_func=self.ani_init , interval=interval)
        self.df = df
        self.number_of_columns = df.shape[1] #num colonne
        self.number_of_points_per_line = df.shape[0]  #num righe
        self.column_index = 0   #verrà incrementato ogni volta che plottiamo una curva
        self.current_column = df.columns[self.column_index]   #tiene conto della colonna in cui ci troviamo
        self.point_index = 0  # verrà incrementato ogni qual volta che plottiamo un punto di una curva
        self.lines = [] # lista di Line2D
        
        for i in range(self.number_of_columns):
            self.lines += self.ax.plot([], [], label = f"Rate window: {self.df.columns[i]}")

    def ani_init(self): 
        # get max of df
        self.ax.set_xlim(0, self.df.index.max())
        self.ax.set_ylim(0, self.df.max().max())
        return self.lines

    def ani_update(self, frame):
        
        # curva = colonna

        # verifichiamo che point_index non sia maggiore del numero di punti per linea
        if self.point_index >= self.number_of_points_per_line:  # vede a che punto sono nella colonna. Se finisce la colonna
            self.point_index = 0                                # risetta l'indice a zero
            self.column_index += 1                              # passa alla colonna successiva
            self.current_column = self.df.columns[self.column_index]   # continuando a tenere conto di dove si trova


        # estraggo i dati che voglio plottare (aggiungo un punto in più ogni volta)
        column_data_y = self.df[self.current_column].iloc[:self.point_index]
        column_data_x = self.df.index[:self.point_index]

        # aggiungo un punto alla curva corrente che corrisponde alla colonna
        self.lines[self.column_index].set_data(column_data_x, column_data_y)

        self.point_index += 1

        print(f"frame: {frame} - column: {self.current_column} - point: {self.point_index} y size: {len(column_data_y)}")

        
        #self.lines[0].set_data(self.xdata[0:frame], self.ydata[0:frame])
        #ax.set_xlim(0, frame/10)
        return self.lines
            

if __name__ == "__main__":
    
    data = InputHandler.read_transients_from_pkl("/home/vito/picts_gif/tests/test_data/test.pkl")
    
    print(data.shape)

    # print(data[819.900].iloc[0:5])
    # 1 Definire la figura e gli assi
    fig, ax = plt.subplots(1,1)
    hp = PictsSpectrumPlot(ax=ax, df=data)
    plt.show()