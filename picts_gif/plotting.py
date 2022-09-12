import re
from timeit import repeat
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# 1 Definire la figura e gli assi
fig, ax = plt.subplots(1,1)

# 2 Definisci dei contenitori per i dati
xdata, ydata = [], []  #li prendo dal dataframe
lines = ax.plot(xdata, ydata)

# 3 Definire un metodo init() che viene chiamato all'inizio 
# all'inizio dell'animazione e che puoi usare per inizializzare 
# Deve ritornare: list[matplotlib.lines.Line2D]
def init():
    xdata.clear()
    ydata.clear()
    ax.set_ylim(-1, 1)
    return lines

# il grafico (titolo, labels..)
# 4 Definire un metodo update() che viene chiamato ad ogni frame
def update(frame):
    # frame <int>: conta il numero di frame 
    xdata.append(frame/10)
    ydata.append(np.sin(frame/10))
    lines[0].set_data(xdata, ydata)
    ax.set_xlim(0, frame/10)
    return lines

# quanto veloce è l'animazione in termini di frame per secondo
# quanti frames animare 
# ... 
# https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html
# fig, func, frames=None, init_func=None, fargs=None, save_count=None, *, cache_frame_data=True, **kwargs
ani = FuncAnimation(fig, update, 
                  #  frames = 20,
                    init_func=init , interval = 10)

plt.show()