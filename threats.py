import numpy as np
import common
import converter


class Threat:
    radar_id: int = 0
    location: None
    emitters = None

    def __init__(self, threatList):
        emitterSize = None

        self.radar_id = threatList[common.THREAT_ID]
        self.location = np.array([threatList[common.THREAT_LOCATION][common.THREAT_XCOORD], threatList[common.THREAT_LOCATION]
                                  [common.THREAT_YCOORD], threatList[common.THREAT_LOCATION][common.THREAT_ZCOORD]], dtype=int, order='C')
        isMultipleEmitters = isinstance(
            threatList[common.THREAT_EMITTERS], list)
        if(isMultipleEmitters == True):
            emitterSize = threatList[common.THREAT_EMITTERS].__len__()
        else:
            emitterSize = 1
        self.emitters = convertEmitterJsonToArray(
            threatList[common.THREAT_EMITTERS], emitterSize)


def convertEmitterJsonToArray(emitterList, emitterSize):
    modeSize = 0
    emitters = [None]*emitterSize
    emitterNode = None

    for emmiterIndex in range(0, emitterSize):
        if(emitterSize > 1):
            emitterNode = emitterList[emmiterIndex]
        else:
            emitterNode = emitterList

        isMultipleModes = isinstance(emitterNode[common.THREAT_MODES], list)
        if(isMultipleModes == True):
            modeSize = emitterNode[common.THREAT_MODES].__len__()
        else:
            modeSize = 1

        emitters[emmiterIndex] = np.zeros(
            [modeSize, common.THREAT_EMITTERMODES_SIZE], dtype=float, order='C')
        for modeIndex in range(0, modeSize):
            if(isMultipleModes == True):
                modeNode = emitterNode[common.THREAT_MODES][modeIndex]
            else:
                modeNode = emitterNode[common.THREAT_MODES]

            emitters[emmiterIndex][modeIndex] = [
                emitterNode[common.THREAT_EMITTER_ID],
                modeNode[common.THREAT_MODEID],
                converter.convertRadarTypeStringToInt(
                    modeNode[common.THREAT_TYPE]),
                modeNode[common.THREAT_PEAKPOWER],
                modeNode[common.THREAT_GAIN],
                modeNode[common.THREAT_ERP] if modeNode[common.THREAT_ISERP] == True else converter.convertToErp(
                    modeNode[common.THREAT_PEAKPOWER], modeNode[common.THREAT_GAIN]),
                modeNode[common.THREAT_FREQ],
                modeNode[common.THREAT_PRF],
                modeNode[common.THREAT_PW],
                modeNode[common.THREAT_RANGE],
                modeNode[common.THREAT_ALT]
            ]

    return emitters


def convertThreatJsonToClass(jsonThreatDict):
    jsonThreatList = jsonThreatDict[common.THREAT_THREATS]
    threatClass = [None]*jsonThreatList.__len__()

    for idx, jsonThreat in enumerate(jsonThreatList):
        threatClass[idx] = Threat(jsonThreat)

    return threatClass
