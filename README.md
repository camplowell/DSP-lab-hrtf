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

### SOFA structure
We are currently using data from MIT_KEMAR
Data set: https://sofacoustics.org/data/database/mit/
Website: https://3d3a.princeton.edu/3d3a-lab-head-related-transfer-function-database

Measurement positions:
- Radius: 76cm
- 72 azimuths: [0, 5, 10, ..., 355]
- 9 elevations: [-57, -30, -15, 0, 15, 30, 45, 60, 75]
- Positional: []

Sofar Inspect
GLOBAL_Conventions : SOFA
GLOBAL_Version : 1.0
GLOBAL_SOFAConventions : SimpleFreeFieldHRIR
GLOBAL_SOFAConventionsVersion : 1.0
GLOBAL_APIName : ARI SOFA API for Matlab/Octave
GLOBAL_APIVersion : 1.1.1
GLOBAL_ApplicationName : ARI converter
GLOBAL_ApplicationVersion :
GLOBAL_AuthorContact : piotr@majdak.com
GLOBAL_Comment : Converted by Piotr Majdak (piotr@majdak.com) and Michael Mihocic, Acoustics Research Institute, OeAW
GLOBAL_DataType : FIR
GLOBAL_History : Converted from the MIT database
GLOBAL_License : This HRTF data is provided without any usage restrictions. It is requested that you cite Gardner and Martin (1995) when using this data for research or commercial applications.
GLOBAL_Organization : MIT Media Lab
GLOBAL_References : Gardner, W. G., and Martin, K. D. (1995). "HRTF measurements of a KEMAR," J Acoust Soc Am 97, 3907-3908.
GLOBAL_RoomType : free field
GLOBAL_Origin : http://sound.media.mit.edu/resources/KEMAR.html
GLOBAL_DateCreated : 1999-11-16 20:01:52
GLOBAL_DateModified : 2020-03-24 13:46:08
GLOBAL_Title : HRTF
GLOBAL_DatabaseName : MIT
GLOBAL_ListenerShortName : KEMAR, normal pinna
ListenerPosition : (I=1, C=3)
  [0. 0. 0.]
ListenerPosition_Type : cartesian
ListenerPosition_Units : metre
ReceiverPosition : (R=2, C=3, I=1)
  [[ 0.    0.09  0.  ]
   [ 0.   -0.09  0.  ]]
ReceiverPosition_Type : cartesian
ReceiverPosition_Units : metre
SourcePosition : (M=710, C=3)
SourcePosition_Type : spherical
SourcePosition_Units : degree, degree, metre
EmitterPosition : (E=1, C=3, I=1)
  [0. 0. 0.]
EmitterPosition_Type : cartesian
EmitterPosition_Units : metre
ListenerUp : (I=1, C=3)
  [0. 0. 1.]
ListenerView : (I=1, C=3)
  [1. 0. 0.]
ListenerView_Type : cartesian
ListenerView_Units : metre
Data_IR : (M=710, R=2, N=512)
Data_SamplingRate : 44100.0
Data_SamplingRate_Units : hertz
Data_Delay : (I=1, R=2)
  [0. 0.]

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

## Resources

[SOFA database](https://www.sofaconventions.org/mediawiki/index.php/Files)
