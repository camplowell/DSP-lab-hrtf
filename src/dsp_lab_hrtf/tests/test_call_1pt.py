import sofar as sf
import numpy as np
import matplotlib.pyplot as plt
import wave
import pyaudio
import struct
import time
from scipy.signal import lfilter, lfilter_zi
from dsp_lab_hrtf.barycentric import BarycentricInterpolator
from dsp_lab_hrtf.ring_buffers import Accumulator
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

def nearest_dot(point, c_array):
    dist_index = np.zeros((c_array.shape[0],1))
    norm_point = np.linalg.norm(point)
    point = point/norm_point

    for i, pos in enumerate(c_array):
        c_norm = np.linalg.norm(c_array[i,:])
        if c_norm == 0:
            dist_index[i] = -1
            continue
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

def make_white(LEN):
    num_samples = LEN
    white_data = np.random.normal(0, 1, size=LEN)

    return white_data

def file_handle(filename):
    sofa = sf.read_sofa(filename)
    data = sofa.Data_IR
    pos = sofa.SourcePosition
    pos_array = polar2cart(pos)

    return data, pos, pos_array

def rotator(points):
    pos_index = np.zeros((points,3))
    for i in range(points):
        ii = 2*np.pi * i / points
        x = np.cos(ii)
        y = np.sin(ii)
        z = 0
        t = .1
        pos_index[i,:] = [x+t,y-t,z]
    return pos_index

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
    while True:
        for i_pos in pos_index:
            current_pos_i = i_pos
            time.sleep(0.1)

except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()