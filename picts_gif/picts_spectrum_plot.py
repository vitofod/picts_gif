from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt
import pandas as pd

#There are many ways to implement animations in matplotlib.
#I have chosen to use classes. 
# The constructor initializes the class by setting the parameters of the plot and those that will animate it.

#The ani_init method fires every time the animation starts. 
#Since the animation can repeat itself, ani_init can be called multiple times.

#The ani_update method is called on each new frame.
#With each invocation, the state of the animation changes.

#The save method is used to save a .gif file of the animation.


class PictsSpectrumPlot:
    
    """
  PictsSpectrumPlot handles animation of PICTS spectrum graphs.
  
  .............................
  Attributes:
  
  fig            : `~matplotlib.figure.Figure`
                  The figure object used to get needed events, such as draw or resize.
        
  ax             : ~matplotlib.axes.Axes
                  The axes object used to get needed events, such as set axis in a graph.
  
  df             : pd.Dataframe
                  Normalized current transient dataframe from InputHandler

  interval       : float
                  Parameter, delay between frames in ms 
 ................................
  Methods:
  
  ani_init(self): 
    manage the animation to start and end. When repeat = True, the method is called at the end of each animation to start it all over again.
    In ani_init the graphical elements that will accompany all the animation and the logic that allows the interruption of the animation are initialized.
    ani_init is a method called only internally to this class, and is essential to the functioning of the FuncAnim class.
    
  ani_update(self):
    ani_update is called by the __init__ method of the PictsSpectrumPlot class and is passed as an attribute to matplotlib's FuncAnimation class. 
    The method is called at each frame. The first argument will be the next value in frames.
    ani_update is a method called only internally to this class, and is essential to the functioning of the FuncAnim class               
  """
    
    def __init__(
        self, 
        fig : plt.figure, 
        ax : plt.axes, 
        df : pd.DataFrame, 
        interval : float = 1.          #interval = delay between frames
        ):
        if not isinstance(df, pd.DataFrame): raise TypeError("Problem with input dataframe")
        if not isinstance(interval, float): raise TypeError("Interval: not a number")
        self.ax = ax
        self.df = df
        self.ax.set_title("Picts Spectrum")
        
        #FunctionAnimation is the Matplotlib class around which everything revolves. 
        #For a better understanding of its use, please refer to the relevant documentation
        #https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html?highlight=funcanimation#matplotlib.animation.FuncAnimation
        self.func_anim = FuncAnimation(
            fig,
            self.ani_update,         #ani_update and ani_init they are part of the architecture with which FuncAnimation is built
            init_func=self.ani_init , #I recommend the detailed documentation at the link for greater understanding
            interval=interval,        
            save_count = 1500         #This index defines the upper limit of the saved frames when calling the method to save the animation
            )
        
        self.number_of_columns = df.shape[1]                     #number of columns in dataframe
        self.number_of_points_per_line = df.shape[0]             #number of rows in dataframe
        self.column_index = 0                                    #it will be incremented every time we plot a curve
        self.current_column = df.columns[self.column_index]      #takes into account the column we are in
        self.point_index = 0                                     #it will be incremented every time we plot a point of a curve
                                                
        self.scatter = None
        self.count=0
        
        self.lines = []                                          #lista di Line2D
        for i in range(self.number_of_columns):                  #Here it is initialized with two lists that will contain the x, y elements of the axes,
                                                                 #and a label that will be updated at each frame
            self.lines += self.ax.plot([], [], label = f"Rate window: {self.df.columns[i]}")

    #Each animation starts and ends by calling this method. 
    #When repeat = True, the method is called at the end of each animation to start it all over again
    def ani_init(self) -> list: 
        """
        ani_init handles the start and the ends of each animation of PICTS spectrum graphs.
        ani_init is called by the __init__ method of the PictsSpectrumPlot class and is passed as an attribute to matplotlib's FuncAnimation class. 
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
        #These settings allow me to automatically center the figure in the graph, regardless of the transient data
        self.ax.set_xlim(
            self.df.index.min() - self.df.index.min()/10, 
            self.df.index.max() + self.df.index.max()/10
            )
        self.ax.set_ylim(
            self.df.min().min() - self.df.min().min()/10, 
            self.df.max().max() + self.df.max().max()/10
            )
        self.ax.set_xlabel('Temperature (K)')
        self.ax.set_ylabel('PICTS signal (a.u.)')
        
        #lines is the iterable that carries information between the various methods. It is a list that at each cycle is filled with all the information to be plotted
        return self.lines

    #for each frame of the animation the class calls this method
    def ani_update(self, frame) -> list:
        """
        ani_update handles each frames of the animation of PICTS spectrum graphs.
        ani_update is called by the __init__ method of the PictsSpectrumPlot class and is passed as an attribute to matplotlib's FuncAnimation class. 
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
        #If I am at the last column of the dataframe and if the number of points I have plotted is greater than or equal to the number of points I had to plot
        if self.current_column == self.df.columns[-1] and self.point_index >= self.number_of_points_per_line:
            self.func_anim.event_source.stop()
            return self.lines

        

        # we have to verify that point_index is not greater than the number of points per line
        if self.point_index >= self.number_of_points_per_line:  # see where I am in the column. If the column ends
            self.point_index = 0                                # resets the index to zero
            self.column_index += 1                              # move to the next column
            self.current_column = self.df.columns[self.column_index]   # continuing to keep track of where it is


        # I extract the data I want to plot (I add an extra point each time)
        column_data_y = self.df[self.current_column].iloc[:self.point_index]
        column_data_x = self.df.index[:self.point_index]
        
       

        # I add a point to the current graph
        self.lines[self.column_index].set_data(column_data_x, column_data_y)

        self.point_index += 1

        return self.lines
    
    #save the animation in a .gif file
    def save(self, output_file_path):
        print(f"Saving animation {output_file_path}")
        self.func_anim.save(output_file_path, writer=PillowWriter(fps=30) )
            
