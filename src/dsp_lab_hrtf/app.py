import argparse
import multiprocessing
import typing
from importlib import resources
from multiprocessing.synchronize import Event
from pathlib import Path


def main():
    args = parser.parse_args()
    audio_path: Path = args.audio
    hrtf_path: Path = args.hrtf
    print(audio_path, hrtf_path)


parser = argparse.ArgumentParser(
    prog="hrtf",
    description="An implementation of head-related transfer functions",
)
parser.add_argument(
    "-a",
    "--audio",
    type=Path,
    help="The audio file to play; should be a PCM .wav file",
)
parser.add_argument(
    "-f",
    "--hrtf",
    type=Path,
    default=resources.files("dsp_lab_hrtf.data").joinpath(
        "mit_kemar_normal_pinna.sofa"
    ),
    help="The head-related transfer function to use; should be a '.sofa' file.",
)


class HasMain(typing.Protocol):
    def main(self, stop: Event): ...


def run(main: HasMain, *aux: HasMain):
    from multiprocessing import Process

    stop = multiprocessing.Event()
    processes: list[Process] = list()
    for m in aux:
        p = Process(
            name=type(m).__name__,
            target=m.main,
            args=(stop,),
        )
        p.start()
        processes.append(p)
    print("Press ^C to exit.")
    try:
        main.main(stop)
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
