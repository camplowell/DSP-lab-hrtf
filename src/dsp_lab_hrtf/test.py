import sofar as sf
import numpy as np
import matplotlib.pyplot as plt

def polar2cart (p_array):
    c_array = np.zeros(p_array.shape)
    i =0

    while i< p_array.shape([0]):
        r = p_array[i,2]
        theta = p_array[i,0]
        phi = p_array[i,1]

        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)

        c_array[i,:] = [x,y,z]

        i += 1

    return c_array

filenames = ["data\mit_kemar_normal_pinna.sofa",
             ]


sofa_guy = sf.read_sofa(filenames[0])

data = sofa_guy.Data_IR

pos = sofa_guy.SourcePosition

pos_array = polar2cart(pos)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.scatter(pos_array[:,0],pos_array[:,1], pos_array[:,2])
plt.show()
