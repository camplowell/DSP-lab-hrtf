from ctypes import Array, c_double
from dataclasses import dataclass, field
import numpy as np
from functools import cached_property

class Context:
    """Shared context between the GUI and the audio processing thread."""
    def __init__(self, query_pos: Array[c_double]):
        self._query_buf = query_pos

    @cached_property
    def query_pos(self):
        return np.frombuffer(self._query_buf)
