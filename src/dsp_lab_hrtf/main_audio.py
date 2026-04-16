import numpy as np

from dsp_lab_hrtf.audio_process import AudioProcess


class AudioMain(AudioProcess):
    def setup(self): ...
    def callback(self, out: np.ndarray, frame_count: int): ...
