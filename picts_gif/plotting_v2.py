import re
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class HarryPlotter:
    def __init__(self, ax, interval = 10, xdata=[], ydata=[]):
        self.ax = ax
        self.ax.set_title("Harry Plotter")
        self.func_anim = FuncAnimation(fig, self.ani_update, init_func=self.ani_init , interval = interval)
        self.lines = self.ax.plot([], [])
        self.xdata = np.array(range(0, 1000))
        self.ydata = np.sin(self.xdata)

    def ani_init(self): 
        self.ax.set_ylim(-1, 1)
        return self.lines

    def ani_update(self, frame):
        self.lines[0].set_data(self.xdata[0:frame], self.ydata[0:frame])
        ax.set_xlim(0, frame/10)
        return self.lines
            

# 1 Definire la figura e gli assi
fig, ax = plt.subplots(1,1)
hp = HarryPlotter(ax=ax)
plt.show()