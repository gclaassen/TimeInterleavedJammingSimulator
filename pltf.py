import numpy as np
import ast
import converter
import common


class Platform:
    rcs: int = 0
    flight_path = None

    def __init__(self, platformList):
        self.rcs = platformList[common.PLF_PLATFORM][common.PLF_RCS]
        self.flight_path = convertPlatformJsonToArray(
            platformList[common.PLF_PLATFORM][common.PLF_FLIGHTPATH])


def convertPlatformJsonToArray(jsonPlatformDict):
    fpArr = np.empty(shape=(jsonPlatformDict.__len__()), dtype=[(common.PLF_XCOORD,int),(common.PLF_YCOORD,int),(common.PLF_ZCOORD,int),(common.PLF_SPEED,int)], order='C')
    for idx, fp in enumerate(jsonPlatformDict):
        fpArr[idx][common.PLF_XCOORD] = fp[common.PLF_XCOORD]
        fpArr[idx][common.PLF_YCOORD] = fp[common.PLF_YCOORD]
        fpArr[idx][common.PLF_ZCOORD] = fp[common.PLF_ZCOORD]
        fpArr[idx][common.PLF_SPEED] = fp[common.PLF_SPEED]
    return fpArr
