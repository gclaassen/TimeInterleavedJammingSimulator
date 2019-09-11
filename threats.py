import numpy as np
import common

class Threat:
    radar_id: int = 0
    location: None
    emitters = None

    def __init__(self, threatList):
        emitterSize = None

        self.radar_id = threatList[common.THREAT_ID]
        self.location = np.array([threatList[common.THREAT_LOCATION][common.THREAT_XCOORD],threatList[common.THREAT_LOCATION][common.THREAT_YCOORD],threatList[common.THREAT_LOCATION][common.THREAT_ZCOORD]], dtype=int, order='C')
        isMultipleEmitters = isinstance(threatList[common.THREAT_EMITTERS], list)
        if(isMultipleEmitters == True):
            emitterSize = threatList[common.THREAT_EMITTERS].__len__()
        else:
            emitterSize = 1
        self.emitters = convertEmitterJsonToArray(threatList[common.THREAT_EMITTERS], emitterSize)

def convertEmitterJsonToArray(emitterList, emitterSize):
    #TODO: loop through emitters and check multiple modes, create empty array, add modes into array
    # emmArr = np.empty(shape=(emitterList.__len__(), common.PLF_FLIGHTPATH_SIZE), dtype=int, order='C')
    return 1



def convertThreatJsonToClass(jsonThreatDict):
    jsonThreatList = jsonThreatDict[common.THREAT_THREATS]
    threatClass = [None]*jsonThreatList.__len__()

    for idx, jsonThreat in enumerate(jsonThreatList):
        threatClass[idx] = Threat(jsonThreat)

    return threatClass