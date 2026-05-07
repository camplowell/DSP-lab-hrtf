import argparse
import multiprocessing
import typing
from importlib import resources
from multiprocessing.synchronize import Event
from pathlib import Path
import sofar
from ctypes import c_double
from scipy import signal

from .context import Context
from .main_gui import Gui
from .main_audio import AudioMain
from .ring_buffers import WaveFile
from .barycentric import BarycentricEncoding
from .resampler import resample_hrtf

from .data import audio_clips, sofa_files

def main():
    # multiprocessing.set_start_method("spawn")
    args = parser.parse_args()
    audio_path = args.audio

    # Search for the audio file
    with resources.as_file(resources.files(audio_clips)) as clip_root:
        if clip_root.joinpath(audio_path).exists():
            audio_path = clip_root.joinpath(audio_path)
        else:
            audio_path = Path(audio_path)

    # Search for hrtf file
    hrtf_path: Path = args.hrtf
    with resources.as_file(resources.files(sofa_files)) as sofa_root:
        if sofa_root.joinpath(hrtf_path).exists():
            hrtf_path = sofa_root.joinpath(hrtf_path)
        else:
            hrtf_path = Path(hrtf_path)

    # Move the query_pos array into shared memory
    query_array = multiprocessing.RawArray(c_double, 3)
    query_array[0] = 1
    context = Context(query_array)
    print(hrtf_path)
    print(audio_path)

    # Download wav file in mono
    wavefile = WaveFile.from_file(str(audio_path)).mix_to_mono()
    wavefile.samples = signal.resample(wavefile.samples, int(len(wavefile.samples) * 16000 / wavefile.sample_rate))
    wavefile.sample_rate = 16000

    print(wavefile.sample_rate)
    # Download sofa file resampled to wav file sampling rate
    sofa = sofar.read_sofa(str(hrtf_path))
    new_sofa = resample_hrtf(sofa, wavefile.sample_rate)

    # Set up Audio and Gui processes
    audio = AudioMain(
        wavefile, 
        BarycentricEncoding(new_sofa),
    )
    run(audio, Gui, context=context)


parser = argparse.ArgumentParser(
    prog="hrtf",
    description="An implementation of head-related transfer functions",
)
parser.add_argument(
    "-a",
    "--audio",
    type=str,
    default = "author.wav",
    help="The audio file to play; should be a PCM .wav file",
)
parser.add_argument(
    "-f",
    "--hrtf",
    type=str,
    default="hrtf b_nh172.sofa",
    help="The head-related transfer function to use; should be a '.sofa' file.",
)


class HasMain(typing.Protocol):
    def main(self, stop: Event): ...


def run(main: HasMain, *aux: HasMain, context: Context):
    from multiprocessing import Process
    stop = multiprocessing.Event()
    processes: list[Process] = list()
    for m in aux:
        p = Process(
            name=type(m).__name__,
            target=m.main,
            args=(stop, context),
        )
        p.start()
        processes.append(p)
    print("Press ^C to exit.")
    try:
        main.main(stop, context)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        import time

        timeout = time.monotonic() + 0.5
        for p in processes:
            if (remaining := timeout - time.monotonic()) > 0:
                p.join(remaining)
        if len(uncooperative := list(filter(lambda p: p.is_alive(), processes))) > 0:
            print("The following tasks failed to terminate cooperatively:")
            for p in uncooperative:
                print(f"\t{p.name}")
                p.terminate()
        for p in processes:
            p.close()
    print("Done.")
