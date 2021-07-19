import numpy as np
import math

radars = np.array([
    [0.337,     503.337,    0,      0,      0],
    # [0.25,       407.25,    0,      0,      0]
    # [0.5,       466.5,      0,      0,      0]
    [25,        345,        0,      0,      0],
    # [0.175,     200.175,    0,      0,      0],
    # [5,         517,        0,      0,      0],
    # [0.9,       20.9,       0,      0,      0],
    # [25,        525,        0,      0,      0],
    # [5,         55,         0,      0,      0],
    # [0.5,       380.2,      0,      0,      0],
    # [3,         52.9,       0,      0,      0],
    # [0.5,       400.5,      0,      0,      0],
    # [5,         130,        0,      0,      0],
    # [6.5,       672.5,      0,      0,      0],
    # [0.45,      450.45,     0,      0,      0],
    # [1.55,      501.55,     0,      0,      0],
    # [10.88,     921.88,     0,      0,      0],
    # [0.4,       93,         0,      0,      0],
    # [3.55,      30,         0,      0,      0],
    # [10,        50,         0,      0,      0]
    ])

# convert from us to s
# radars[:, 0] = radars[:, 0]*math.pow(10,-6)
# radars[:, 1] = radars[:, 1]*math.pow(10,-6)
radars[:, 4] = radars[:, 1] - radars[:, 0]

# get prf
radars[:,2] = 1/(radars[:,1]*math.pow(10,-6))

# get duty cycle
radars[:,3] = radars[:, 0]/radars[:, 1]

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

coincidenceof2on1 = (1-(radars[1, 1] - (radars[0, 0] + radars[1, 0]))/(radars[1, 1]))*radars[0, 2]
print("Total coincidences between radar 1 and 2: {0}".format(coincidenceof2on1))


coincidenceof2on1_1 =  ( ( (radars[0,0] + radars[1,0]) ) )/(radars[0,4]) * radars[0,2]
coincidenceof2on1_2 = coincidenceof2on1_1 + ( radars[1,1] )/(radars[0,1]) * radars[0,2]
print("GCN Total coincidences between radar 1 and 2: {0}".format(coincidenceof2on1_2))

pass