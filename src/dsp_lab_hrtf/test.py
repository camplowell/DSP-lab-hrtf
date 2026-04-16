import sofar as sf
import numpy as np
import matplotlib.pyplot as plt

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
    print(point)

    for i, pos in enumerate(c_array):
        dist = np.vecdot(point, c_array[i,:])
        dist_index[i] = dist
    
    point_index = dist_index.argmax()

    return point_index


filenames = ["data\mit_kemar_normal_pinna.sofa",
             "data\hrtf b_nh169.sofa",
             "data\hrtf b_nh172.sofa"]


sofa_guy = sf.read_sofa(filenames[0])

data = sofa_guy.Data_IR

pos = sofa_guy.SourcePosition
print(pos.shape)

pos_array = polar2cart(pos)

guess_point = [1,0,0]

near_point = nearest_polar([5,11], pos)
near_point_dot = nearest_dot(guess_point, pos_array)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.scatter(pos_array[:,0],pos_array[:,1], pos_array[:,2])
ax.scatter(pos_array[near_point_dot,0],pos_array[near_point_dot,1],pos_array[near_point_dot,2], color='red')
ax.scatter(guess_point[0],guess_point[1],guess_point[2], color='green')

ax.set(xlabel='x',
       ylabel='y',
       zlabel='z')
plt.show()



print(near_point)

print('Index',near_point, ':', pos[near_point,:])
print('Index dot',near_point_dot, ':', pos[near_point_dot,:])





