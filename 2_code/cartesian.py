import math
import common
import numpy as np
import mathRadar as radarmath

def initializeCartesianArray(rows):
    return np.zeros(shape=(rows), dtype=[(common.XCOORD, float), (common.YCOORD, float), (common.ZCOORD, float), (common.DISTANCE, float), (common.ANGLE_AZI, float), (common.ANGLE_ELEV, float),  (common.PLF_SPEED, float), (common.TIME, float), (common.TOTAL_TIME, float)], order='C')

def sphericalCoordinatesCalculation (node1, node2):
    x = (node2[common.XCOORD] - node1[common.XCOORD])
    y = (node2[common.YCOORD] - node1[common.YCOORD])
    z = (node2[common.ZCOORD] - node1[common.ZCOORD])

    r = displacement3dSpace(node1, node2)

    azi = math.degrees(math.atan2(y, x))

    elev = math.degrees(math.atan2(math.sqrt(math.pow(x, 2) + math.pow(y, 2)), z))

    return [r, azi, elev]

def polarToCartesian(r, azi, elev):
    x = r * math.sin(elev) * math.cos(azi)
    y = r * math.sin(elev) * math.sin(azi)
    z = r * math.cos(elev)

    return [x, y, z]

def displacement3dSpace (node1, node2):
    x = (node2[common.XCOORD] - node1[common.XCOORD])
    y = (node2[common.YCOORD] - node1[common.YCOORD])
    z = (node2[common.ZCOORD] - node1[common.ZCOORD])

    return math.sqrt(
        math.pow(x, 2) +
        math.pow(y, 2) +
        math.pow(z, 2))

def flightTimeBetweenCartesianPoints_us(r, velocity_mps):
    return radarmath.convertTime_SecondsToMicroseconds(r/velocity_mps)


def displacementInTime(velocity_mps, time_us):
    return velocity_mps*radarmath.convertTime_MicrosecondsToSeconds(time_us)

def updateCoord(prevNode, dispNode):
    x = (prevNode[common.XCOORD] + dispNode[common.XCOORD])
    y = (prevNode[common.YCOORD] + dispNode[common.YCOORD])
    z = (prevNode[common.ZCOORD] + dispNode[common.ZCOORD])

    return [x, y, z]
