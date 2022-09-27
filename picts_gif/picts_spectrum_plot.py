#import re
#import numpy as np
#from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

#from picts_gif.input_handler import InputHandler

class PictsSpectrumPlot:
    def __init__(self, fig, ax, df, interval = 0.01): #interval = delay between frames
        self.ax = ax
        self.df = df
        self.ax.set_title("Picts Spectrum")
        self.func_anim = FuncAnimation(fig, self.ani_update, init_func=self.ani_init , interval=interval)
        self.number_of_columns = df.shape[1] #num colonne
        self.number_of_points_per_line = df.shape[0]  #num righe
        self.column_index = 0   #verrà incrementato ogni volta che plottiamo una curva
        self.current_column = df.columns[self.column_index]   #tiene conto della colonna in cui ci troviamo
        self.point_index = 0  # verrà incrementato ogni qual volta che plottiamo un punto di una curva
        self.lines = [] # lista di Line2D
        self.scatter = None
        self.count=0
        
        for i in range(self.number_of_columns):
            self.lines += self.ax.plot([], [], label = f"Rate window: {self.df.columns[i]}")

    def save(self, output_dir):
        output_file = output_dir.joinpath("spectrum.gif")
        print(f"Saving animation in {output_file}")
        self.func_anim.save(output_file,writer=PillowWriter(fps=50) )

    def ani_init(self): 
        # get max of df
        self.ax.set_xlim(self.df.index.min() - self.df.index.min()/10, self.df.index.max() + self.df.index.max()/10)
        self.ax.set_ylim(self.df.min().min() - self.df.min().min()/10, self.df.max().max() + self.df.max().max()/10)
        return self.lines

    def ani_update(self, frame):
        
        # termination condition
        if self.current_column == self.df.columns[-1] and self.point_index >= self.number_of_points_per_line:
            self.func_anim.event_source.stop()
            return self.lines

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

        #if self.scatter is not None:
        #  self.scatter.remove()
        #self.scatter = self.ax.scatter(x=self.current_column, y=column_data_y.iloc[self.point_index])

        #try:
        #    print(f"frame: {frame} - column: {self.current_column} - point: {self.point_index} y size: {len(column_data_y)} - y_value: {column_data_y.iloc[-1]}")
        #except Exception as e:
        #    pass
        
        #self.lines[0].set_data(self.xdata[0:frame], self.ydata[0:frame])
        #ax.set_xlim(0, frame/10)



        return self.lines
            

""" if __name__ == "__main__":
    
    path = '/home/vito/picts_gif/tests/test_data/data.tdms'
    dic_path = '/home/vito/picts_gif/tests/test_data/dictionary.json'
    #data = InputHandler.read_transients_from_pkl("/home/vito/picts_gif/tests/test_data/test.pkl")
    data = InputHandler.read_transients_from_tdms(path, dic_path)
    normalized_transient = InputHandler.normalized_transient(data, dic_path)
    picts, gates = InputHandler.from_transient_to_PICTS_spectrum(normalized_transient, dic_path)
    
    
    fig, ax = plt.subplots(1,1)
    hp = PictsSpectrumPlot(fig=fig, ax=ax, df=picts)
    plt.show() """