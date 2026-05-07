## Take all the hrtfs
## Sample them to the audio file rate
import numpy as np
from scipy.signal import resample
from scipy import interpolate
from tqdm import tqdm

def resample_hrtf(hrtf, audio_sr):
    hrtf_sr = getattr(hrtf, "Data_SamplingRate")
    ir = getattr(hrtf, "Data_IR")
    
    prop = audio_sr / hrtf_sr

    new_len = int(round(len(ir[0,0,:]) * prop))
    instances = len(ir[:,0,0])

    resample_arr = np.empty((instances, 2, new_len), dtype=np.float32)

    for i in tqdm(np.arange(0, instances), "Resampling HRTF"):
        resample_arr[i,0,:] = resample(ir[i,0,:], new_len)
        resample_arr[i,1,:] = resample(ir[i,1,:], new_len)
    

    setattr(hrtf, "Data_IR", resample_arr)
    setattr(hrtf, "Data_SamplingRate", audio_sr)
    return hrtf

def interp_hrtf(hrtf, audio_sr):
    hrtf_sr = getattr(hrtf, "Data_SamplingRate")
    ir = getattr(hrtf, "Data_IR")

    prop = audio_sr / hrtf_sr

    hrtf_len = int(len(ir[0,0,:]))
    new_len = int(round(len(ir[0,0,:]) * prop))
    hrtf_block = np.arange(0,hrtf_len)
    instances = len(ir[:,0,0])

    interp_arr = np.empty((instances, 2, new_len), dtype=np.float32)

    for i in tqdm(np.arange(0, instances), "Resampling HRTF"):
        interp0 = interpolate.interp1d(hrtf_block, ir[i,0,:], kind='cubic')
        interp1 = interpolate.interp1d(hrtf_block, ir[i,1,:], kind='cubic')
        interp_arr[i,0,:] = interp0(np.linspace(0, hrtf_len, new_len))
        interp_arr[i,1,:] = interp1(np.linspace(0, hrtf_len, new_len))

    setattr(hrtf, "Data_IR", interp_arr)
    setattr(hrtf, "Data_SamplingRate", audio_sr)
    return hrtf
