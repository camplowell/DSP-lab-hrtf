import sofar as sf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure
import wave
import pyaudio
import struct
import tkinter as Tk
import time
from dsp_lab_hrtf.barycentric import BarycentricInterpolator
from dsp_lab_hrtf.ring_buffers import Accumulator
from dsp_lab_hrtf.test_funcs import cart2polar, polar2cart, rotator


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
ax.plot([0,1], [0,0], [0,0], 'g-')
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
               from_=-0.5, to=0.985,
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
               from_=80, to=-30,
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


























# READ IN WAV FILE
wavefile = 'data/author.wav'
wf          = wave.open(wavefile, 'rb')
RATE        = wf.getframerate()
WIDTH       = wf.getsampwidth()
LEN         = wf.getnframes() 
CHANNELS    = wf.getnchannels()

wf_in = wf.readframes(LEN)
wf_data = np.array(struct.unpack('h'*LEN, wf_in))

# GRAB SOFA
sofa = sf.read_sofa("data/hrtf b_nh172.sofa")
interpolator = BarycentricInterpolator(sofa)

# BUILD ARC
steps = 360
pos_index = rotator(steps)

# INITIALIZE
BLOCKLEN = 512 * 16
sec_per_pos = 0.01
current_pos_i = [1,0,0]

current_pos_i = np.array([1,0,0], dtype=np.float64)
cache_pos_i = current_pos_i
ir = interpolator.query(current_pos_i)
current_ir = interpolator.query(current_pos_i)

accumulate = Accumulator(current_ir.T.shape, current_ir.dtype)

def callback(in_data, frame_count, time_info, status):
    global j, current_pos_i, cache_pos_i, ir

    t = time.perf_counter()

    if not((current_pos_i == cache_pos_i).all()):
        ir = interpolator.query(current_pos_i)
        cache_pos_i = current_pos_i

    G = 5

    ret = np.zeros((BLOCKLEN, 2))
    for i in range(0, BLOCKLEN):

        in_pt = wf_data[(j+i) % LEN]
        in_ir = in_pt * ir * G
        ret[i] = accumulate.splat(in_ir.T)
    
    """ in_pt = wf_data[j]
    in_ir = in_pt * ir * G
    ret = accumulate.splat(in_ir.T)
 """
    j = (j + BLOCKLEN) % LEN

    output_block = np.empty(2*BLOCKLEN, dtype=np.int16)
    output_block[0::2] = np.clip(ret[:,0], -32768, 32767).astype(np.int16)
    output_block[1::2] = np.clip(ret[:,1], -32768, 32767).astype(np.int16)

    t1 = time.perf_counter() - t
    if t1 > .01:
        print('Too long', t1)

    return (output_block.tobytes(), pyaudio.paContinue)

p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format = PA_FORMAT,
    channels = 2,
    rate = int(RATE),
    input = False,
    output = True,
    frames_per_buffer = BLOCKLEN,
    stream_callback = callback)

j = 0
stream.start_stream()

try:
    while CONTINUE:
        current_pos_i = np.array([hold['x'], hold['y'], hold['z']])
        time.sleep(0.1)
        root.update()

except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()