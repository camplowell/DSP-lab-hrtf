from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(init=False, slots=True)
class WaveFile:
    path: str
    sample_rate: int
    channels: int
    length: int
    samples: np.ndarray

    def __init__(self, path: str | Path):
        import wave

        path = str(path)

        self.path = path
        with wave.open(path, "rb") as wf:
            self.sample_rate = wf.getframerate()
            self.channels = wf.getnchannels()
            self.length = wf.getnframes()
        self.samples = np.empty((0), np.float32)

    def load_samples(self):
        import wave

        with wave.open(self.path, "rb") as wf:
            w = wf.getsampwidth()

            pcm = np.frombuffer(
                wf.readframes(wf.getnframes()),
                dtype=np.dtype(f"<i{w}" if w > 1 else "<u1"),
            ).reshape(
                (wf.getnframes(), wf.getnchannels())
                if wf.getnchannels() > 1
                else (wf.getnframes(),)
            )
        self.samples = np.divide(pcm, 2 ** (8 * w - 1))
        if w == 1:
            self.samples -= 127

    def get(self, start: int, N: int, *, out: np.ndarray | None = None) -> np.ndarray:
        start %= len(self)
        out = (
            out
            if out is not None
            else np.ndarray(
                (N,)
                if len(self.samples.shape) == 1  #
                else (N, self.samples.shape[1])
            )
        )
        remaining = out[:N]
        while remaining.shape[0] > 0:
            part = min(len(self) - start, remaining.shape[0])
            remaining[:part] = self.samples[start : start + part]
            remaining = remaining[part:]
            start = (start + part) % len(self)
        return out

    def __getitem__(self, index: int):
        return self.samples[index]

    def __len__(self):
        return self.length

    def duration(self):
        return self.length / self.sample_rate
