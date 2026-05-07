from __future__ import annotations

import numpy as np
from numpy.typing import DTypeLike

import numba
from numba.experimental import jitclass

@jitclass
class Accumulator:
    samples: numba.float32[:, ::1]  # pyright: ignore[reportInvalidTypeForm, reportGeneralTypeIssues]
    i_write: int

    def __init__(self, shape: tuple[int, int]):
        self.samples = np.zeros(shape, np.float32)
        self.i_write = 0

    def splat(self, data: np.ndarray) -> float:
        """Add a single sample's contribution to the accumulator, returning the convolved sample."""
        part1: int = min(data.shape[0], self.samples.shape[0] - self.i_write)
        self.samples[self.i_write : self.i_write + part1] += data[:part1]

        part2: int = data.shape[0] - part1
        if part2 > 0:
            self.samples[:part2] += data[part1:]

        ret = self.samples[self.i_write].copy()
        self.samples[self.i_write] = 0

        self.i_write = (self.i_write + 1) % self.samples.shape[0]
        return ret

    def convolve(
        self,
        kernels: np.ndarray,
        out: np.ndarray,
    ) -> np.ndarray:
        for i in range(kernels.shape[0]):
            out[i] = self.splat(kernels[i].T)
        return out


class WaveFile:
    __slots__ = ("playhead", "samples", "sample_rate")
    playhead: int
    samples: np.ndarray
    sample_rate: int

    def __init__(self, samples: np.ndarray, sample_rate: int):
        self.samples = samples
        self.sample_rate = sample_rate
        self.playhead = 0

    @staticmethod
    def from_file(file: str):
        import wave

        with wave.open(file, "rb") as wf:
            sample_rate = wf.getframerate()
            pcm = np.frombuffer(
                wf.readframes(wf.getnframes()),
                np.dtype(f"<i{wf.getsampwidth()}"),
            ).reshape((-1, wf.getnchannels()))
        samples = pcm / (2 ** (8 * wf.getsampwidth() - 1))
        return WaveFile(samples, sample_rate)

    def mix_to_mono(self):
        new_samples = np.mean(self.samples, axis=1).reshape((-1, 1))
        return WaveFile(new_samples, self.sample_rate)

    def next(self, n: int):
        assert n < self.samples.shape[0]
        out = np.ndarray((n, self.samples.shape[1]))
        part1 = min(n, self.samples.shape[0] - self.playhead)
        out[:part1] = self.samples[self.playhead : self.playhead + part1]

        if (part2 := n - part1) > 0:
            out[part1:] = self.samples[:part2]
        self.playhead = (self.playhead + n) % self.samples.shape[0]
        return out
