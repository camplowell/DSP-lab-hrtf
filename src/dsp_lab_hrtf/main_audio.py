import numpy as np
from dataclasses import dataclass, field

from dsp_lab_hrtf.audio_process import AudioProcess
from dsp_lab_hrtf.ring_buffers import Accumulator, WaveFile
from dsp_lab_hrtf.barycentric import BarycentricEncoding
from dsp_lab_hrtf.context import Context

@dataclass(slots=True)
class AudioMain(AudioProcess):
    context: Context = field(init=False)
    query_pos: np.ndarray = field(init=False)
    x_src: WaveFile
    encoding: BarycentricEncoding
    accum: Accumulator = field(init=False)

    def setup(self, context: Context):
        self.context = context
        self.query_pos = self.context.query_pos.copy()
        self.accum = Accumulator((128, 2), np.float32)
        self.sample_rate = self.x_src.sample_rate
        self.frames_per_buffer = 256

    def callback(self, out: np.ndarray, frame_count: int):
        x = self.x_src.next(frame_count)
        irs = np.empty((frame_count, 2, 64), np.float32)
        next_query_pos = self.context.query_pos
        for i, direction in zip(
            range(frame_count),
            np.linspace(
                self.query_pos,
                self.context.query_pos,
                frame_count,
            ),
        ):
            irs[i] = self.encoding.query(
                direction, x[i]
            )[:, :64]
        self.accum.convolve(irs, out)
        self.query_pos[:] = next_query_pos
