from turtle import color
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import json
import pandas as pd


#There are many ways to implement animations in matplotlib.
#I have chosen to use classes. 
# The constructor initializes the class by setting the parameters of the plot and those that will animate it.

#The ani_init method fires every time the animation starts. 
#Since the animation can repeat itself, ani_init can be called multiple times.

#The ani_update method is called on each new frame.
#With each invocation, the state of the animation changes.

#The save method is used to save a .gif file of the animation.

class PictsTransientPlot:
    """
  PictsTransientPlot handles animation of PICTS transient graphs.
  
  .............................
  Attributes:
  
  fig            : `~matplotlib.figure.Figure`
                  The figure object used to get needed events, such as draw or resize.
        
  ax             : ~matplotlib.axes.Axes
                  The axes object used to get needed events, such as set axis in a graph.
                  
  ax             : str
                  The path to the json file.
  
  transient_df   : pd.Dataframe
                  Normalized current transient dataframe from InputHandler
  
  gates_list     : np.array
                  Float array with (t1, t2) rate window interval
  
  interval       : float
                  Parameter, delay between frames in ms 
  """
  
    
    def __init__(
      self, 
      fig : plt.figure, 
      ax : plt.axes, 
      conf_file_path : str, 
      transient_df : pd.DataFrame, 
      gates_list : np.array, 
      interval : float = 1.          #interval = delay between frames in ms
      ): 
      
      
      with open(conf_file_path, "r") as pfile:
         self.configuration = json.load(pfile)
         
      if not isinstance(transient_df, pd.DataFrame): raise TypeError("Problem with input dataframe")
      if not isinstance(gates_list, np.ndarray): raise TypeError("Problem with gates_list array")
      if not isinstance(interval, float): raise TypeError("Problem with the interval parameter")
      
      self.ax = ax
        
        #FunctionAnimation is the Matplotlib class around which everything revolves. 
        #For a better understanding of its use, please refer to the relevant documentation
        #https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html?highlight=funcanimation#matplotlib.animation.FuncAnimation
      self.func_anim = FuncAnimation(
          fig, 
          self.ani_update,                    #ani_update and ani_init they are part of the architecture with which FuncAnimation is built. 
                                              #I recommend the detailed documentation at the link for greater understanding
          init_func=self.ani_init , 
          interval=interval, 
          repeat=True,                        #when the animation is finished, it restart from beginning
          frames=len(transient_df.columns),   #total number of images that make up the animation. Coincides with the number of transients to plot.
          save_count = 1500                   #This index defines the upper limit of the saved frames when calling the method to save the animation
          )
        
      self.transient_df = transient_df
      self.gates_list = gates_list
      self.gate_index = -1                    #It starts from -1 as a way to avoid the "index out of bounds" exception.
      self.column_index = 0                   #it will be incremented every time a transient is inserted in the frame list. 
                                              #In this way I can always know where i am in the dataframe
                                             
      self.current_column = self.transient_df.columns[self.column_index]   # Returns the name of the column that is about to be plotted
        
        
      #Lines is a list of the elements that are iterated in the animation. 
      #Here it is initialized with two lists that will contain the x, y elements of the axes, and a title that will be updated at each frame
      self.lines = []
      self.lines += self.ax.plot([], [], label = f"Temperature: {self.transient_df.columns[self.column_index]}")
        
      self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        
      #Scatter and Arrow are two graphical elements that I initialize and that will subsequently be defined and inserted overlapping the graph
      self.scatter = None  
      self.arrow = None
 
    #Each animation starts and ends by calling this method. 
    #When repeat = True, the method is called at the end of each animation to start it all over again
    def ani_init(self) -> list: 
        """
        ani_init handles the start and the ends of each animation of PICTS transient graphs.
        ani_init is called by the __init__ method of the PictsTransientPlot class and is passed as an attribute to matplotlib's FuncAnimation class. 
        In ani_init the graphical elements that will accompany all the animation and the logic that allows the interruption of the animation are initialized.
  
       ......................................................
         Return:
         - lines:
            a list of parameters through which FuncAnim creates the graphic environment of the animation   
         ......................................................
         REFERENCES:
         For a better understanding of its use, please refer to the following documentation
         - https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html?highlight=funcanimation#matplotlib.animation.FuncAnimation
         ......................................................
         ......................................................
        """

        # I define some parameters for the plot
        #These settings allow me to automatically center the figure in the graph
        t_init = self.configuration['t1_min']
        beta = self.configuration['beta']
        n_windows = self.configuration['n_windows']
        self.ax.set_xlim(
          -0.015, 
          t_init + beta*t_init*n_windows
          )
        self.ax.set_ylim(
          self.transient_df.index.min(), 
          self.transient_df.max().max()/2
          )
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Normalized Current (a.u)')
        
        #column_index must be re-initialized because if the graph restarts, all parameters must return to their starting values
        self.column_index = 0 

        #every time the graph restarts, it means that I am showing a new rate window, 
        # so I have to advance with the values ​​(t1, t2)
        self.gate_index += 1
        gate = self.gates_list[self.gate_index]
        
        #We have to imagine the dataframe with the index coinciding with the x axis, 
        #and each column constitutes a y axis (an axis for each temperature value at which the current was measured)
        #I check which column I am plotting
        self.current_column = self.transient_df.columns[self.column_index]
        
        #I add to the plot some vertical dashed lines that will indicate the interval of the rate window
        self.ax.axvline(x = gate[0], label = f't1 - {round(gate[0], 2)}', color=self.colors[self.gate_index], linestyle="dashed")
        self.ax.axvline(x = gate[1], label = f't2 - {round(gate[1], 2)}', color=self.colors[self.gate_index], linestyle="dashed")

        column_name = self.transient_df.columns[self.column_index]

        #lines is the iterable that carries information between the various methods. It is a list that at each cycle is filled with all the information to be plotted
        
        return self.lines

    #for each frame of the animation the class calls this method
    def ani_update(self, frame) -> list:
        """
        ani_update handles each frames of the animation of PICTS transient graphs.
        ani_init is called by the __init__ method of the PictsTransientPlot class and is passed as an attribute to matplotlib's FuncAnimation class. 
        The method is called at each frame. The first argument will be the next value in frames.
        .............................
        Attributes:
        - frame:
             The first argument will be the next value in frames
           ......................................................
         Return:
         - lines:
            a list of argument that will be the next values in frames  
         ......................................................
         REFERENCES:
         For a better understanding of its use, please refer to the following documentation
         - https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html?highlight=funcanimation#matplotlib.animation.FuncAnimation
         ......................................................
         ......................................................
        """
      
        # if the following conditions are met, the animation is finished:
        #if all the pairs (t1, t2) have been plotted and if I am at the last column of the dataframe
        if self.gate_index == len(self.gates_list) - 1 and self.current_column == self.transient_df.columns[-1]:
            self.func_anim.event_source.stop()
            return self.lines     #I always return the list lines

       
        self.ax.set_title(f"Temperature: {self.current_column} K")
            
        #Each frame is accessed internally, from the self.lines list, 
        #to the corresponding elements and the set_data method is called on that object. 
        #This updates the current frame
        column_data_y = self.transient_df[self.current_column]
        column_data_x = self.transient_df.index
        self.lines[0].set_data(column_data_x, column_data_y)

        # handle scatter and arrow points
        gate = self.gates_list[self.gate_index] # (t1,t2), correspond to the i-th gate, which does not change for the entire duration of the animation
        indexes = self.transient_df.index.get_indexer(gate, method = 'backfill') # the corresponding indexes of the Temperature column are accessed
        ys = column_data_y.iloc[indexes] 
        #Basically I created the pair of points (t1, y1) and (t2, y2). I need it to make two rods appear inside the graph

        #If at each frame I did not cancel the previous scatters, the graph would be overcrowded with points
        if self.scatter is not None:
          self.scatter.remove()
        self.scatter = self.ax.scatter(x=gate, y=ys, color = 'red', s=50)

        # Same thing for the arrow element
        if self.arrow is not None:
          self.arrow.remove()
        self.arrow = self.ax.annotate( 
                                      text="", 
                                      xy = (-0.01,ys.iloc[0]),
                                      xytext = (-0.01,ys.iloc[1]),
                                      arrowprops=dict(arrowstyle='<->', color = 'red', linewidth=2)
                                      ) #This are a trick to make a moving arrow appear in the graph. 
                                        #It is better understandable first by looking at the gif than by explaining it

        

        #When I have plotted all the data in a column, I can increment the position of the column I was in
        if self.column_index < len(self.transient_df.columns) - 1:
          self.column_index += 1
        self.current_column =  self.transient_df.columns[self.column_index]

        #I return the updated lines
        return self.lines 
      
    
    def save(self, output_dir):
      output_file = output_dir.joinpath("transient.gif")
      print(f"Saving animation {output_file}")
      self.func_anim.save(output_file, writer= PillowWriter(fps=30))
            

