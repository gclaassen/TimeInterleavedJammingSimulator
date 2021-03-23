import numpy as np
import ast
import common
import math

class Platform:
    rcs: int = 0
    flightPath = None
    nodes = 0
    timeStart = 0
    timeStop = 0

    def __init__(self, platformList):
        self.rcs = platformList[common.PLF_PLATFORM][common.PLF_RCS]
        [timeStart, timeStop, self.flightPath] = convertPlatformJsonToArray(
            platformList[common.PLF_PLATFORM][common.PLF_FLIGHTPATH])


def convertPlatformJsonToArray(jsonPlatformDict):
    # iTimeStart -> just for completeness sake
    iTimeStart = 0
    iTotalNodeTime = 0
    arrFlightPath = np.zeros(shape=(jsonPlatformDict.__len__()), dtype=[(common.XCOORD, int), (common.YCOORD, int), (common.ZCOORD, int), (common.DISTANCE, float), (common.PLF_SPEED, int), (common.TIME, float)], order='C')
    for idx, fp in enumerate(jsonPlatformDict):
        arrFlightPath[idx][common.XCOORD] = fp[common.XCOORD]
        arrFlightPath[idx][common.YCOORD] = fp[common.YCOORD]
        arrFlightPath[idx][common.ZCOORD] = fp[common.ZCOORD]
        arrFlightPath[idx][common.PLF_SPEED] = fp[common.PLF_SPEED]

        if(idx == 0):
            arrFlightPath[idx][common.TIME] = 0
            arrFlightPath[idx][common.DISTANCE] = 0
        elif(idx > 0):
            [arrFlightPath[idx][common.TIME], arrFlightPath[idx][common.DISTANCE]] = nodeFlightTime(arrFlightPath[idx-1],arrFlightPath[idx])
            
        iTotalNodeTime += arrFlightPath[idx][common.TIME]

    return iTimeStart, iTotalNodeTime, arrFlightPath

# calculate distance in 3d space:
## sqrt( ( x2 - x1 )^2 + ( y2 - y1 )^2 + ( y2 - y1 )^2 )
# meaure time
## t = d/v 
def nodeFlightTime(prevNode, currentNode):
    distance = distance3dSpace(prevNode, currentNode)
    return [distance/currentNode[common.PLF_SPEED], distance]

def distance3dSpace (node1, node2):
    return math.sqrt(math.pow((node2[common.XCOORD] - node1[common.XCOORD]), 2) +
    math.pow((node2[common.YCOORD] - node1[common.YCOORD]), 2) +
    math.pow((node2[common.ZCOORD] - node1[common.ZCOORD]), 2))
