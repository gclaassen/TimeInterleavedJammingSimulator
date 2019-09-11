import numpy as np
import ast
import converter
import common

class Platform:
    rcs: int = 0
    flight_path = None

    def __init__(self, platformList):
        self.rcs = platformList[common.PLF_PLATFORM][common.PLF_RCS]
        self.flight_path = convertPlatformJsonToArray(platformList[common.PLF_PLATFORM][common.PLF_FLIGHTPATH])

def convertPlatformJsonToArray(jsonPlatformDict):
    fpArr = np.empty(shape=(jsonPlatformDict.__len__(), common.PLF_FLIGHTPATH_SIZE), dtype=int, order='C')
    for idx, fp in enumerate(jsonPlatformDict):
        fpArr[idx] = [fp[common.PLF_XCOORD],fp[common.PLF_YCOORD],fp[common.PLF_ZCOORD], fp[common.PLF_SPEED]]
    return fpArr
