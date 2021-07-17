import numpy as np
import math

radars = np.array([
    [0.337, 503, 0],
    [0.587, 1507, 0],
    [6.4, 25, 0],
    [25, 320, 0],
    [0.175, 200, 0],
    [5, 512, 0],
    [0.9, 20, 0],
    [25, 500, 0],
    [4.5, 50, 0],
    [0.5, 379.8, 0],
    [3, 49.9, 0],
    [0.5, 400, 0],
    [5, 125, 0],
    [8, 666, 0],
    [0.45, 450, 0],
    [1.55, 500, 0],
    [10.88, 911, 0],
    [0.4, 92.6, 0],
    [3.55, 26.45, 0],
    [10, 40, 0]])

# convert from us to s
radars[:, 0] = radars[:, 0]*math.pow(10,-6)
radars[:, 1] = radars[:, 1]*math.pow(10,-6)

# get prf
radars[:,2] = 1/radars[:,1]

# get total coincidences
coincidenceTotal = 0
for radarIdx in range(0, len(radars)-1):
    freqCalc1 = 1
    freqCalc2 = 1
    for radarItemIdx in range (0, radarIdx-1):
        tempFreqCalc1 =  (radars[radarItemIdx, 1] - (radars[radarIdx, 0] + radars[radarItemIdx, 0]))/(radars[radarItemIdx, 1])
        freqCalc1 = tempFreqCalc1 * freqCalc1

    for radarItemIdx2 in range(0, len(radars)):
        if(radarItemIdx2 != radarIdx):
            tempFreqCalc2 =  (radars[radarItemIdx2, 1] - (radars[radarIdx, 0] + radars[radarItemIdx2, 0]))/(radars[radarItemIdx2, 1])
            freqCalc2 = tempFreqCalc2 * freqCalc2


    coincidenceTotal = coincidenceTotal + (freqCalc1 - freqCalc2)*radars[radarIdx, 2]

print("Total coincidences: {0}".format(coincidenceTotal))

pass