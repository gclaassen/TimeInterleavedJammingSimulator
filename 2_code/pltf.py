import numpy as np
import ast
import common
import math
import mathRadar as radarmath
import cartesian

class cPlatform:
    rcs: int = 0
    flightPath = None
    nodes = 0
    timeStart_us = 0
    timeStop_us = 0

    def __init__(self, platformList):
        self.rcs = platformList[common.PLF_PLATFORM][common.PLF_RCS]
        [self.timeStart_us, self.timeStop_us, self.flightPath] = convertPlatformJsonToArray(
            platformList[common.PLF_PLATFORM][common.PLF_FLIGHTPATH])


def convertPlatformJsonToArray(jsonPlatformDict):
    # iTimeStart -> just for completeness sake
    iTimeStart = 0
    iTotalNodeTime = 0

    arrFlightPath = cartesian.initializeCartesianArray(jsonPlatformDict.__len__())

    for idx, fp in enumerate(jsonPlatformDict):
        arrFlightPath[idx][common.XCOORD] = fp[common.XCOORD]
        arrFlightPath[idx][common.YCOORD] = fp[common.YCOORD]
        arrFlightPath[idx][common.ZCOORD] = fp[common.ZCOORD]
        arrFlightPath[idx][common.PLF_SPEED] = fp[common.PLF_SPEED]

        if(idx == 0):
            arrFlightPath[idx][common.TIME] = 0
            arrFlightPath[idx][common.DISTANCE] = 0
            arrFlightPath[idx][common.ANGLE_AZI] = 0
            arrFlightPath[idx][common.ANGLE_ELEV] = 0

        elif(idx > 0):
            [ arrFlightPath[idx][common.DISTANCE], arrFlightPath[idx][common.ANGLE_AZI], arrFlightPath[idx][common.ANGLE_ELEV] ] = cartesian.sphericalCoordinatesCalculation(arrFlightPath[idx-1], arrFlightPath[idx])

            arrFlightPath[idx][common.TIME] = cartesian.flightTimeBetweenCartesianPoints_us(arrFlightPath[idx][common.DISTANCE], arrFlightPath[idx][common.PLF_SPEED])

        iTotalNodeTime += arrFlightPath[idx][common.TIME]

        arrFlightPath[idx][common.TOTAL_TIME] = iTotalNodeTime

    return [iTimeStart, iTotalNodeTime, arrFlightPath]
