import tkinter as Tk
from multiprocessing.synchronize import Event

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .context import Context

class Gui(Tk.Tk):
    interval: int = 16
    context: Context
    updating: bool = False

    def __init__(self, stop: Event, context: Context):
        super().__init__()
        self.context = context
        self.stop_event = stop
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # Hold buffer to sync changes in cartesian and polar
    hold = {'x': 1,
            'y': 0,
            'z': 0,
            'az': 0,
            'el': 0}
    

    def updatePlot(self, event):
        if self.updating:
            return
        self.updating = True

        # Get variable data
        x = self.pos_x.get()
        y = self.pos_y.get()
        z = self.pos_z.get()
        az = self.pos_az.get()
        el = self.pos_el.get()

        # Determine which variables changed on the GUI and sync the rest
        if (az != self.hold['az']) or (el != self.hold['el']):
            self.hold['x'], self.hold['y'], self.hold['z'] = polar2cart([az, el])
            self.hold['az'], self.hold['el'] = az, el
            self.pos_x.set(self.hold['x'])
            self.pos_y.set(self.hold['y'])
            self.pos_z.set(self.hold['z'])
            self.hold['x'], self.hold['y'], self.hold['z'] = self.pos_x.get(), self.pos_y.get(), self.pos_z.get()
        else:
            self.hold['az'], self.hold['el'] = cart2polar([x, y, z])
            self.hold['x'], self.hold['y'], self.hold['z'] = x, y, z
            self.pos_az.set(self.hold['az'])
            self.pos_el.set(self.hold['el'])
            self.hold['az'], self.hold['el'] = self.pos_az.get(), self.pos_el.get()

        # Vector line points in selected direction
        self.vec_line.set_data([0,x], [0,y])
        self.vec_line.set_3d_properties([0,z])

        # Draw, lower updating flag, pass data out
        self.fig.canvas.draw()
        self.updating = False
        np.frombuffer(self.context.query_pos)[:] = self.hold['x'], self.hold['y'], self.hold['z']
    
    def layout(self):
        matplotlib.use('TkAgg')

        self.title('HRTF Position Selector')

        # TK VARIABLES INIT
        self.pos_x = Tk.DoubleVar()
        self.pos_y = Tk.DoubleVar()
        self.pos_z = Tk.DoubleVar()
        self.pos_az = Tk.DoubleVar()
        self.pos_el = Tk.DoubleVar()

        self.pos_x.set(1)
        self.pos_y.set(0)
        self.pos_z.set(0)

        # FIGURE INIT
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, projection="3d")

        [self.vec_line] = ax.plot([0, 0], [0, 0], [0, 0], "r-")
        ax.plot([0, 1], [0, 0], [0, 0], "g-")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.view_init(elev=30, azim=160, roll=0)

        self.refs = np.array(
            [
                [x, y, z]
                for x in [0.25, -0.25]
                for y in [0.25, -0.25]
                for z in [0.25, -0.25]
            ]
        )

        self.S_X = Tk.Scale(self, length=500,
                    orient='horizontal',
                    from_=-1, to=1,
                    resolution=0.1,
                    command=self.updatePlot,
                    label='X Position',
                    variable=self.pos_x)
        self.S_Y = Tk.Scale(self, length=500,
                    orient='horizontal',
                    from_=-1, to=1,
                    resolution=0.1,
                    command=self.updatePlot,
                    label='Y Position',
                    variable=self.pos_y)
        self.S_Z = Tk.Scale(self, length=500,
                    orient='horizontal',
                    from_=-0.5, to=0.985,
                    resolution=0.1,
                    command=self.updatePlot,
                    label='Z Position',
                    variable=self.pos_z)


        self.S_A = Tk.Scale(self, length=200,
                    orient='vertical',
                    from_=-180, to=180,
                    resolution=0.1,
                    command=self.updatePlot,
                    variable=self.pos_az)
        self.S_E = Tk.Scale(self, length=200,
                    orient='vertical',
                    from_=80, to=-30,
                    resolution=0.1,
                    command=self.updatePlot,
                    variable=self.pos_el)



        canvas = FigureCanvasTkAgg(self.fig, master=self)
        C1 = canvas.get_tk_widget()

        # self.B_Q = Tk.Button(self, text='Quit', command=my_quit)


        ## GRID
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        C1.grid(row=0, column=0, columnspan=4)
        self.S_X.grid(row=1, column=0)
        self.S_Y.grid(row=2, column=0)
        self.S_Z.grid(row=3, column=0)
        self.S_A.grid(row=1, column=1, rowspan=3)
        self.S_E.grid(row=1, column=2, rowspan=3)
        # self.B_Q.grid(row=4, column=2)

        self.fig.tight_layout()


    @staticmethod
    def main(stop: Event, context: Context):
        gui = Gui(stop, context)
        gui.layout()
        gui.check_stop()
        gui.mainloop()
          
    def on_close(self):
        self.stop_event.set()
        self.quit()
        self.destroy()
    
    def check_stop(self):
        if self.stop_event.is_set():
            self.destroy()
        self.after(100, self.check_stop)


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