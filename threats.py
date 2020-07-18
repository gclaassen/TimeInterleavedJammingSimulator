import numpy as np
import common
import converter
import math


class Threat:
    radar_id: int = 0
    radar_name = None
    location: None
    emitters = None
    emitter_current = None
    mode_current = None
    detect: None
    jammer: None
    za: float=0
    ma: float=0
    Pj: float=0

    def __init__(self, threatList):
        emitterSize = None

        self.radar_id = threatList[common.THREAT_ID]
        self.radar_name = threatList[common.THREAT_NAME]
        self.location = np.array((
            threatList[common.THREAT_LOCATION][common.XCOORD],
            threatList[common.THREAT_LOCATION][common.YCOORD],
            threatList[common.THREAT_LOCATION][common.ZCOORD],
            threatList[common.THREAT_LOCATION][common.THREAT_RANGE],
            threatList[common.THREAT_LOCATION][common.THREAT_ALT]
            ), dtype=
                    [
                        (common.XCOORD,int),
                        (common.YCOORD,int),
                        (common.ZCOORD,int),
                        (common.THREAT_RANGE, int),
                        (common.THREAT_ALT, int)
                    ], order='C')
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

        emitters[emmiterIndex] = np.zeros(modeSize, dtype=
                                        [
                                            (common.THREAT_EMITTER_ID,int),
                                            (common.THREAT_MODEID,int),
                                            (common.THREAT_TYPE,int),
                                            (common.THREAT_PEAKPOWER, int),
                                            (common.THREAT_GAIN, int),
                                            (common.THREAT_ERP, int),
                                            (common.THREAT_FREQ, int),
                                            (common.THREAT_PRI, float),
                                            (common.THREAT_PW, float)
                                        ], order='C')
        for modeIndex in range(0, modeSize):
            if(isMultipleModes == True):
                modeNode = emitterNode[common.THREAT_MODES][modeIndex]
            else:
                modeNode = emitterNode[common.THREAT_MODES]

            emitters[emmiterIndex][modeIndex][common.THREAT_EMITTER_ID] = emitterNode[common.THREAT_EMITTER_ID]
            emitters[emmiterIndex][modeIndex][common.THREAT_MODEID] = modeNode[common.THREAT_MODEID]
            emitters[emmiterIndex][modeIndex][common.THREAT_TYPE] = converter.convertRadarTypeStringToInt(modeNode[common.THREAT_TYPE])
            emitters[emmiterIndex][modeIndex][common.THREAT_PEAKPOWER] = modeNode[common.THREAT_PEAKPOWER]
            emitters[emmiterIndex][modeIndex][common.THREAT_GAIN] = modeNode[common.THREAT_GAIN]
            emitters[emmiterIndex][modeIndex][common.THREAT_ERP] = modeNode[common.THREAT_ERP] if modeNode[common.THREAT_ISERP] == True else converter.convertToErp(modeNode[common.THREAT_PEAKPOWER], modeNode[common.THREAT_GAIN])
            emitters[emmiterIndex][modeIndex][common.THREAT_FREQ] = modeNode[common.THREAT_FREQ]
            emitters[emmiterIndex][modeIndex][common.THREAT_PRI] = modeNode[common.THREAT_PRI]
            emitters[emmiterIndex][modeIndex][common.THREAT_PW] = modeNode[common.THREAT_PW]

    return emitters


def convertThreatJsonToClass(jsonThreatDict):
    jsonThreatList = jsonThreatDict[common.THREAT_THREATS]
    threatClass = [None]*jsonThreatList.__len__()

    for idx, jsonThreat in enumerate(jsonThreatList):
        threatClass[idx] = Threat(jsonThreat)

    return threatClass

def PriTimeRange(Tstart_ns, Tstop_ns, PRI):
    PriStart = [(Tstart_us//PRI)*PRI] + PRI
    PriStop = [(Tstop_us//PRI)*PRI] + PRI
    totalPulses = math.ceil((PriStop - PriStart)/PRI)

    return [PriStart, PriStop, totalPulses]
