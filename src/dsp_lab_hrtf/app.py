import argparse
from importlib import resources
from pathlib import Path

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


def main():
    args = parser.parse_args()
    audio_path: Path = args.audio
    hrtf_path: Path = args.hrtf
    print(audio_path, hrtf_path)
