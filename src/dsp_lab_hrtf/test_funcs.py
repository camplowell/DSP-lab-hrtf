import numpy as np
import sofar as sf


def polar2cart_matrix (p_array):
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