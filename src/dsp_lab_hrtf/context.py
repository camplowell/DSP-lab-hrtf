from ctypes import c_double
from dataclasses import dataclass
import multiprocessing
import numpy as np

@dataclass(slots=True)
class Context:
    """Shared context between the GUI and the audio processing thread."""
    query_pos: np.ndarray