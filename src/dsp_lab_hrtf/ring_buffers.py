from __future__ import annotations

import numpy as np
from numpy.typing import DTypeLike


class Accumulator:
    __slots__ = ("samples", "i_write")

    def __init__(self, shape: tuple[int, int], dtype: DTypeLike):
        self.samples = np.zeros(shape, dtype)
        self.i_write: int = 0

    def splat(self, data: np.ndarray) -> float:
        """Add a single sample's contribution to the accumulator, returning the convolved sample."""
        assert data.shape[0] <= self.samples.shape[0]
        part1 = min(data.shape[0], self.samples.shape[0] - self.i_write)
        self.samples[self.i_write : self.i_write + part1] += data[:part1]

        if (part2 := data.shape[0] - part1) > 0:
            self.samples[:part2] += data[part1:]

        ret = self.samples[self.i_write]
        self.samples[self.i_write] = 0

        self.i_write = (self.i_write + 1) % self.samples.shape[0]
        return ret
