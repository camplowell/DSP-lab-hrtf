# DSP-lab-hrtf
Final project for ECE-GY 6183

## What is a Head-Related Transfer Function (HRTF)?
The geometry of the human head and body affects sounds as it reaches our ears. This extra information helps the human brain to 'place' sounds in space. Head-related transfer functions aim to capture or approximate this effect.

Usually, they are measured by placing a human or human-shaped object in an anechoic chamber with microphones in each ear, then playing sounds from loudspeakers placed at a variety of angles (and sometimes distances) around the observer. This is then encoded as a set of angle-impulse response pairs. In use, this information is then interpolated when determining how a sound source should be filtered for users with stereo systems such as headphones.


### How is this data stored?
You will most commonly see HRTFs distributed as [.sofa](https://www.sofaconventions.org) files.  
Like many container formats, it can actually store information in a variety of formats, the most common of which are:
- SimpleFreeFieldHRIR: Emitter location-impulse response pairs, measured with an omnidirectional source for a single listener.
- SimpleFreeFieldHRTF: Similar to SimpleFreeFieldHRIR, but stores the transfer function in the frequency domain.
- SimpleFreeFieldHRSOS: Similar to SimpleFreeFieldHRIR, but stores the transfer function as second order sections (SOS).

## Running
This project was developed using Python 3.13.

I generally recommend using [uv](https://docs.astral.sh/uv/) if you need to manage multiple Python versions.

If you do use uv, you can run the project with:
```bash
uv run hrtf
```

in the repository root.

If not, run:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
hrtf
```
