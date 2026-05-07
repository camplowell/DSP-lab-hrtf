## Ok here's what we're trying to make
## This test will output a vector giving
## a new location any time the slider moves at all

import numpy as np
from scipy.signal import butter, freqz
import tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure

def polar2cart(p_array):

    r = 1 #p_array[i,2]
    theta = np.pi * p_array[0]/180
    phi = np.pi * p_array[1]/180

    x = r * np.cos(phi) * np.cos(theta)
    y = r * np.cos(phi) * np.sin(theta)
    z = r * np.sin(phi)

    return x,y,z

def cart2polar(p_array):

    r = np.sqrt(p_array[0]**2 + p_array[1]**2 + p_array[2]**2)

    if r == 0:
        return 0, 0
    
    theta = 180 * np.arctan2(p_array[1],p_array[0]) / np.pi
    phi = 180 * np.arcsin(p_array[2]/r) / np.pi

    return theta, phi



matplotlib.use('TkAgg')

root = Tk.Tk()
root.title('Source position selector')

pos_x = Tk.DoubleVar()
pos_y = Tk.DoubleVar()
pos_z = Tk.DoubleVar()

pos_az = Tk.DoubleVar()
pos_el = Tk.DoubleVar()

pos_x.set(1)
pos_y.set(0)
pos_z.set(0)

fig = matplotlib.figure.Figure()
ax = fig.add_subplot(111, projection='3d')

[vec_line] = ax.plot([0,0], [0,0], [0,0], 'r-')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')


refs = np.array([[x, y, z] 
                 for x in [0.25, -0.25] 
                 for y in [0.25, -0.25] 
                 for z in [0.25, -0.25]])

#ax.scatter(refs[:,0], refs[:,1], refs[:,2], color='blue', s=20, depthshade=False, alpha=1.0)


hold = {'x': 1,
        'y': 0,
        'z': 0,
        'az': 0,
        'el': 0}
updating = False

def my_quit():
    global CONTINUE
    CONTINUE = False
    print('Goodbye')

def updatePlot(event):
    global updating
    if updating:
        return
    updating = True

    x = pos_x.get()
    y = pos_y.get()
    z = pos_z.get()

    az = pos_az.get()
    el = pos_el.get()

    if (az != hold['az']) or (el != hold['el']):
        hold['x'], hold['y'], hold['z'] = polar2cart([az, el])
        hold['az'], hold['el'] = az, el
        pos_x.set(hold['x'])
        pos_y.set(hold['y'])
        pos_z.set(hold['z'])
        hold['x'], hold['y'], hold['z'] = pos_x.get(), pos_y.get(), pos_z.get()
    else:
        hold['az'], hold['el'] = cart2polar([x, y, z])
        hold['x'], hold['y'], hold['z'] = x, y, z
        pos_az.set(hold['az'])
        pos_el.set(hold['el'])
        hold['az'], hold['el'] = pos_az.get(), pos_el.get()

    vec_line.set_data([0,x], [0,y])
    vec_line.set_3d_properties([0,z])

    fig.canvas.draw()

    updating = False

    return None

# WIDGETS
S_X = Tk.Scale(root, length=500,
               orient='horizontal',
               from_=-1, to=1,
               resolution=0.1,
               command=updatePlot,
               label='X Position',
               variable=pos_x)
S_Y = Tk.Scale(root, length=500,
               orient='horizontal',
               from_=-1, to=1,
               resolution=0.1,
               command=updatePlot,
               label='Y Position',
               variable=pos_y)
S_Z = Tk.Scale(root, length=500,
               orient='horizontal',
               from_=-1, to=1,
               resolution=0.1,
               command=updatePlot,
               label='Z Position',
               variable=pos_z)


S_A = Tk.Scale(root, length=200,
               orient='vertical',
               from_=-180, to=180,
               resolution=0.1,
               command=updatePlot,
               variable=pos_az)
S_E = Tk.Scale(root, length=200,
               orient='vertical',
               from_=-90, to=90,
               resolution=0.1,
               command=updatePlot,
               variable=pos_el)



canvas = FigureCanvasTkAgg(fig, master=root)
C1 = canvas.get_tk_widget()

B_Q = Tk.Button(root, text='Quit', command=my_quit)


## GRID
root.rowconfigure(0, weight=3)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.columnconfigure(0, weight=10)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

C1.grid(row=0, column=0, columnspan=4)
S_X.grid(row=1, column=0)
S_Y.grid(row=2, column=0)
S_Z.grid(row=3, column=0)
S_A.grid(row=1, column=1, rowspan=3)
S_E.grid(row=1, column=2, rowspan=3)
B_Q.grid(row=4, column=2)



updatePlot(None)

fig.tight_layout()

CONTINUE = True
while CONTINUE:
    root.update()

