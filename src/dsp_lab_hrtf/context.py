from ctypes import c_double
from dataclasses import dataclass, field
import multiprocessing
import numpy as np


@dataclass(slots=True)
class Context:
    """Shared context between the GUI and the audio processing thread."""
    query_pos: np.ndarray = field(default_factory=lambda: np.array([1,0,0]))

    def __post_init__(self):
        # Move the query_pos array into shared memory
        shared_query = np.frombuffer(multiprocessing.RawArray(c_double, 3))
        shared_query[:] = self.query_pos
        self.query_pos = np.frombuffer(shared_query, dtype=np.float64)