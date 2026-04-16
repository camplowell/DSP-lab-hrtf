import sofar as sf
import numpy as np
import matplotlib.pyplot as plt
import wave
import pyaudio
import struct
import time

def polar2cart (p_array):
    c_array = np.zeros(p_array.shape)
    i =0

    while i< p_array.shape[0]:
        r = 1 #p_array[i,2]
        theta = np.pi * p_array[i,0]/180
        phi = np.pi * p_array[i,1]/180

        x = r * np.cos(phi) * np.cos(theta)
        y = r * np.cos(phi) * np.sin(theta)
        z = r * np.sin(phi)

        c_array[i,:] = [x,y,z]

        i += 1

    return c_array

def nearest_polar(point, p_array):
    dist_index = np.zeros((p_array.shape[0],1))

    for i, [theta,phi,r] in enumerate(p_array):
        dist = np.linalg.norm(np.subtract(point, [theta,phi]))
        dist_index[i] = dist

    point_index = dist_index.argmin()

    return point_index

def nearest_dot(point, c_array):
    dist_index = np.zeros((c_array.shape[0],1))
    norm_point = np.linalg.norm(point)
    point = point/norm_point

    for i, pos in enumerate(c_array):
        c_norm = np.linalg.norm(c_array[i,:])
        dist = np.vecdot(point, c_array[i,:]) / c_norm
        dist_index[i] = dist
    
    point_index = dist_index.argmax()

    return point_index

def conv_data(wf, ir_array, point):
    ir_L = ir_array[point, 0, :]
    ir_R = ir_array[point, 1, :]

    out_L = np.convolve(ir_L, wf)
    out_R = np.convolve(ir_R, wf)

    return out_L, out_R



filenames = ["data\mit_kemar_normal_pinna.sofa",
             "data\hrtf b_nh169.sofa",
             "data\hrtf b_nh172.sofa",
             "data\SCUT_NF_subject0001_measured.sofa"]


sofa_guy = sf.read_sofa(filenames[2])

data = sofa_guy.Data_IR

pos = sofa_guy.SourcePosition
print(pos.shape)

pos_array = polar2cart(pos)

guess_point = [1,0,0]

near_point = nearest_polar([5,11], pos)
near_point_dot = nearest_dot(guess_point, pos_array)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.scatter(pos_array[:,0],pos_array[:,1], pos_array[:,2], alpha=.3)
#current_marker, = ax.plot([0],[0],[0],'o', color='red', markersize=10)

ax.quiver(0, 0, 0,  1, 0, 0,  color='green', length=1.2, label='forward (0° az)')
ax.quiver(0, 0, 0,  0, 0, 1,  color='blue',  length=1.2, label='up (90° el)')
ax.legend()

ax.set(xlabel='x',
       ylabel='y',
       zlabel='z')
#plt.ion()
plt.show()

pos_index = np.zeros((360,3))
for i in range(360):
    x = np.cos(np.deg2rad(i))
    y = np.sin(np.deg2rad(i))
    z = 0
    pos_index[i,:] = [x,y,z]

BLOCKLEN = 256
print(len(pos_index[1]))
mean = 0
std = 1 
num_samples = BLOCKLEN * len(pos_index[0])
white_data = np.random.normal(mean, std, size=num_samples)


wavefile = 'data/author.wav'
wf          = wave.open(wavefile, 'rb')
RATE        = wf.getframerate()
WIDTH       = wf.getsampwidth()
LEN         = wf.getnframes() 
CHANNELS    = wf.getnchannels()

wf_in = wf.readframes(LEN)
wf_data = struct.unpack('h'*LEN, wf_in)
print(RATE)

p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format = PA_FORMAT,
    channels = 2,
    rate = RATE,
    input = False,
    output = True)




""" pos_index = [[1, 0, 0],   # front
             [1, 1, 0],   # front-right
             [0, 1, 0],   # right
             [-1, 1, 0],  # back-right
             [-1, 0, 0],  # back
             [-1, -1, 0], # back-left
             [0, -1, 0],  # left
             [1, -1, 0],  # front-left
             [1, 0, 0],   # back to front
             [1, 0, 0],   # front
             [1, 0, 1],   # front-high
             [0, 0, 1],   # directly above
             [-1, 0, 1],  # back-high
             [-1, 0, 0]   # back
            ] """



for i, i_pos in enumerate(pos_index):

    print(i_pos)
    near_point_dot = nearest_dot(i_pos, pos_array)
    print(near_point_dot)
    out_L, out_R = conv_data(white_data, data, near_point_dot)

    max_val = max(np.max(np.abs(out_L)), np.max(np.abs(out_R)))
    out_L = (out_L / max_val * 32767).astype(np.int16)
    out_R = (out_R / max_val * 32767).astype(np.int16)

    C_LEN = len(out_L)
    print('C_LEN:', C_LEN)
    j = 0
    while j + BLOCKLEN <= C_LEN:
        #white_block = white_data[j : j + BLOCKLEN]

        block_L = out_L[j : j + BLOCKLEN]
        block_R = out_R[j : j + BLOCKLEN]

        output_block = np.zeros(BLOCKLEN * 2, dtype=np.int16)
        output_block[0::2] = block_L
        output_block[1::2] = block_R
        output_bytes = struct.pack('hh'*BLOCKLEN, *output_block)

        stream.write(output_bytes)

        j += BLOCKLEN
    #time.sleep(1)

#plt.ioff()
stream.stop_stream()
stream.close()
p.terminate()