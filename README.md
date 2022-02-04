# Time-Interleaved-Jamming
Time Interleaved Jamming Simulator

## Introduction

The simulated jamming system is heuristic to display the functionality of the time interleaved jammer controller (TIJ) on a self protection jamming platform.
It is assumed that a theoretical PRI tracker is used as ESM does not form part of the hypothesis.
Therefore the parameters of the collected signals received will be ideal and there will be no inaccurate timing predictions.
The jammer will transmit the precise jamming signal characteristics at the intended time with the intended duration in the main beam of the threat radar.
However it will be fruitful in future research to investigate the effectiveness of the TIJ system when less than ideal information are presented, as what can be expected in the real world.

The TIJ controller functionality will be tested through the use of a simulation.
The simulator consist of a main interval loop function and three processing functions within the main loop.
The three processing function consist of the interval coincidence calculator, the interval coincidence sweeper, and the interval threat radar evaluator.

The main function loops through the jamming time intervals correlating to the the flightpath and velocity of the platform.
Each jamming interval time will be 1 second long where only known pulse radar signals will be encountered.
The interval coincidence calculator determines and stores the coincidences with the pulses associated.
The list of coincidences are then processed by the interval coincidence sweeper that determines the high priority pulses at each coincidence depending on the threat evaluation and prioritisation technique employed.

Lastly after the interval each threat is analysed and according to the jamming effectiveness implemented against each CPI is determined to either move up or down a mode.
The post processing time is seen as independent from the jamming intervals in the simulation.
Only a single detection at or above the radar's required probability of detection in an interval is required for the radar to move up to the next mode.
Therefore the jammer needs to prevent detection for each of the CPI without the knowledge of when a CPI starts.

The simulation consist of platform, jammer, and threat parameters and characteristics all configurable in the respective JSON files.


## Argument List

| Command | Description                                      | Example        |
| ------- | ------------------------------------------------ | -------------- |
| -v      | Set visualize to true                            | -v             |
| -p      | Set the jamming bin size to the PRI              | -p             |
| -c      | Set the jamming window to end after the pulse    | -c             |
| -e      | Set to an experimental window size               | -e             |
| -i      | The test and result folder name                  | -i PRITestFolder |
| -m      | The mode weight                                  | -m 0.15        | 
| -z      | The zone assessment weight                       | -z 0.05        |
| -l      | The lethal range weight                          | -l 0.10        |
| -j      | The jamming percentage weight                    | -j 0.7         |
| -b      | Ignore the radar pulses in burnthrough           | -b             |
| -r      | The starting pulses for each radar at each interval starts at random time between 0 and the PRI | -r             |
| -t      | Iterate in coincidence and select highest priority non overlapping pulses otherwise all the pulses of the same radar in coincidence will be selected first before checking the overlap pulses.                    | -t             |


# Requirements
*note: these were the software and hardware that I used to develop and run the TIJ simulator*
## Software
- Python 3.8.3 64-bit
### Pyton Modules
- math
- json
- numpy *
- ast
- scipy *
- matplotlib *
- matplotlib-label-lines *
- spectrum *
- numba *
- multiprocessing
- logging
- time
- tabulate *
- tqdm *

> *install required
> pip install numpy scipy matplotlib matplotlib-label-lines spectrum tabulate tqdm

## PC
- OS: Windows 10 64 bit
- CPU: Intel I5-3750K
- RAM: 8GB
- GPU: NVIDIA ASUS GeForce GTX 1060 Dual OC 6GB GDDR5 1280 Cuda Core
