## Ok here's what we're trying to make
## This test will output a vector giving
## a new location any time the slider moves at all

import numpy as np
from scipy.signal import butter, freqz
import tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure

matplotlib.use('TkAgg')

root = Tk.Tk()
root.title('Source position selector')

pos_a = Tk.DoubleVar()
pos_e = Tk.DoubleVar()

fig = matplotlib.figure.Figure()
ax = fig.add_subplot(111, projection='3d')

def my_quit():
    global CONTINUE
    CONTINUE = False
    print('Goodbye')

def updatePlot(event):
    return None

# Grid config
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.columnconfigure(0, weight=3)  # plot side
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# WIDGETS
canvas = FigureCanvasTkAgg(fig, master=root)
C1 = canvas.get_tk_widget()
C1.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

L_az = Tk.Label(root, text='Azimuth')
L_az.grid(row=0, column=1, sticky=Tk.N, pady=(20,0))
S_A = Tk.Scale(root, orient='vertical', from_=180, to=-180, resolution=1,
               command=updatePlot, variable=pos_a, length=200)
S_A.grid(row=0, column=1, pady=(50,0))

L_el = Tk.Label(root, text='Elevation')
L_el.grid(row=0, column=2, sticky=Tk.N, pady=(20,0))
S_E = Tk.Scale(root, orient='vertical', from_=90, to=-90, resolution=1,
               command=updatePlot, variable=pos_e, length=200)
S_E.grid(row=0, column=2, pady=(50,0))

B_Q = Tk.Button(root, text='Quit', command=my_quit)
B_Q.grid(row=1, column=1, columnspan=2, sticky=Tk.E, padx=(0,10), pady=(10,10))

updatePlot(None)

fig.tight_layout()

CONTINUE = True
while CONTINUE:
    root.update()