from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from multiprocessing.synchronize import Event

from .context import Context

import numpy as np


@dataclass(slots=True)
class AudioProcess(ABC):
    sample_rate: int = field(default=44100, kw_only=True)
    channels: int = field(default=2, kw_only=True)
    frames_per_buffer: int = field(default=0, kw_only=True)
    __input: np.ndarray | None = field(init=False, default=None)

    def __post_init__(self):
        assert not hasattr(self, "__dict__")

    def setup(self, context: Context):
        """Load any additional resources that don't need to be present on other processes"""
        pass

    @abstractmethod
    def callback(self, out: np.ndarray, frame_count: int):
        """Process audio by filling `out`. Raise StopIteration to stop."""
        raise NotImplementedError

    @property
    def mic(self):
        """Get the microphone; raises an AssertionError if the mic was not requested."""
        assert self.__input is not None
        return self.__input

    def main(self, stop: Event, context: Context):
        import pyaudio
        self.setup(context)

        def stream_callback(
            in_data: bytes | None,
            frame_count: int,
            *_,
        ) -> tuple[bytes | None, int]:
            if stop.is_set():
                return None, pyaudio.paComplete
            out = np.zeros(
                (frame_count,)
                if self.channels == 1  #
                else (frame_count, self.channels),
                np.float32,
            )
            if in_data:
                self.__input = np.frombuffer(in_data, like=out)
            self.callback(out, frame_count)
            np.clip(out, -1, 1, out=out)
            out_pcm = np.empty_like(out, dtype=np.int16)
            np.multiply(out, 2**15-1, out=out_pcm, casting="unsafe")
            return out_pcm.tobytes(), pyaudio.paContinue

        stream: pyaudio.Stream | None = None
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                rate=self.sample_rate,
                format=pyaudio.paInt16,
                channels=self.channels,
                input=False,
                output=True,
                stream_callback=stream_callback,
                frames_per_buffer=self.frames_per_buffer,
                start=True,
            )
            stop.wait()
        except KeyboardInterrupt:
            pass
        finally:
            stop.set()
            if stream:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            pa.terminate()
