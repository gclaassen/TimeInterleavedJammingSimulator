import numpy as np
import common
import math
import mathRadar as radmath
import logging

class cThreat:
    # threat parameters
    radar_id: int = 0
    radar_name = None
    location: None
    emitters = None

    # current mode parameters
    emitter_current = None
    mode_current = None
    channel_current = None

    #interval Info
    lIntervalPulseStore = None
    lIntervalPulseCoincidenceStore = None
    lIntervalTIJStore = None

    def __init__(self, threatList):
        emitterSize = None

        self.radar_id = threatList[common.THREAT_ID]
        self.radar_name = threatList[common.THREAT_NAME]
        logging.debug("Threat: %s id: %s",self.radar_name, self.radar_id)
        self.location = np.array((
            threatList[common.THREAT_LOCATION][common.XCOORD],
            threatList[common.THREAT_LOCATION][common.YCOORD],
            threatList[common.THREAT_LOCATION][common.ZCOORD]
            ), dtype=
                    [
                        (common.XCOORD,int),
                        (common.YCOORD,int),
                        (common.ZCOORD,int)
                    ], order='C')
        isMultipleEmitters = isinstance(
            threatList[common.THREAT_EMITTERS], list)
        if(isMultipleEmitters == True):
            logging.debug("Multiple emitters")
            emitterSize = threatList[common.THREAT_EMITTERS].__len__()
        else:
            logging.debug("Single emitter")
            emitterSize = 1
        self.emitters = convertEmitterJsonToArray(
            threatList[common.THREAT_EMITTERS], emitterSize)

        if(self.emitters.__len__() > 0):
            minModeIdx = 0
            modeSize = np.size(self.emitters[0])
            if(modeSize > 1):
                minModeIdx = np.min(np.where(self.emitters[0][:][common.THREAT_MODE_TYPE] == np.min(self.emitters[0][:][common.THREAT_MODE_TYPE])))
            #TODO: currently only cater so a single emitter with single or multiple different modes

            self.mode_current = self.emitters[0][minModeIdx][common.THREAT_MODE_ID]
            self.emitter_current = self.emitters[0][minModeIdx]


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
        logging.debug("Mode Size %s", modeSize)


        emitters[emmiterIndex] = np.zeros(modeSize, dtype=
                                        [
                                            (common.THREAT_EMITTER_ID,int),
                                            (common.THREAT_MODE_ID,int),
                                            (common.THREAT_MODE_TYPE,int),
                                            (common.THREAT_PEAKPOWER_KW, int),
                                            (common.THREAT_AVGPOWER_KW, float),
                                            (common.THREAT_GAIN, int),
                                            (common.THREAT_FREQ_MHZ, int),
                                            (common.THREAT_PRI_US, float),
                                            (common.THREAT_PW_US, float),
                                            (common.THREAT_DUTY_CYCLE, float),
                                            (common.THREAT_CPI, int),
                                            (common.THREAT_PROB_DETECTION, float),
                                            (common.THREAT_PROB_FALSE_ALARM, float),
                                            (common.THREAT_PROB_DETECTION_MIN, float)
                                        ], order='C')
        for modeIndex in range(0, modeSize):

            if(isMultipleModes == True):
                modeNode = emitterNode[common.THREAT_MODES][modeIndex]
            else:
                modeNode = emitterNode[common.THREAT_MODES]

            emitters[emmiterIndex][modeIndex][common.THREAT_EMITTER_ID] = emitterNode[common.THREAT_EMITTER_ID]
            emitters[emmiterIndex][modeIndex][common.THREAT_MODE_ID] = modeNode[common.THREAT_MODE_ID]
            emitters[emmiterIndex][modeIndex][common.THREAT_MODE_TYPE] = modeNode[common.THREAT_MODE_TYPE]
            emitters[emmiterIndex][modeIndex][common.THREAT_PEAKPOWER_KW] = modeNode[common.THREAT_PEAKPOWER_KW]
            emitters[emmiterIndex][modeIndex][common.THREAT_GAIN] = modeNode[common.THREAT_GAIN]
            emitters[emmiterIndex][modeIndex][common.THREAT_FREQ_MHZ] = modeNode[common.THREAT_FREQ_MHZ]
            emitters[emmiterIndex][modeIndex][common.THREAT_PRI_US] = modeNode[common.THREAT_PRI_US]
            emitters[emmiterIndex][modeIndex][common.THREAT_PW_US] = modeNode[common.THREAT_PW_US]
            emitters[emmiterIndex][modeIndex][common.THREAT_DUTY_CYCLE] = radmath.calculateDutyCycle(modeNode[common.THREAT_PW_US], modeNode[common.THREAT_PRI_US])
            emitters[emmiterIndex][modeIndex][common.THREAT_CPI] = modeNode[common.THREAT_CPI]
            emitters[emmiterIndex][modeIndex][common.THREAT_AVGPOWER_KW] = radmath.convertPeakPowerToAvgPower(emitters[emmiterIndex][modeIndex][common.THREAT_PEAKPOWER_KW], emitters[emmiterIndex][modeIndex][common.THREAT_DUTY_CYCLE])
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_DETECTION] = modeNode[common.THREAT_PROB_DETECTION]
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_FALSE_ALARM] = modeNode[common.THREAT_PROB_FALSE_ALARM]
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_DETECTION_MIN] = modeNode[common.THREAT_PROB_DETECTION_MIN]
    return emitters


def convertThreatJsonToClass(jsonThreatDict):
    jsonThreatList = jsonThreatDict[common.THREAT_THREATS]
    threatClass = [None]*jsonThreatList.__len__()

    for idx, jsonThreat in enumerate(jsonThreatList):
        threatClass[idx] = cThreat(jsonThreat)

    return threatClass

def PriTimeRange(Tstart_ns, Tstop_ns, PRI):
    PriStart = [(Tstart_ns//PRI)*PRI] + PRI
    PriStop = [(Tstop_ns//PRI)*PRI] + PRI
    totalPulses = math.ceil((PriStop - PriStart)/PRI)

    return [PriStart, PriStop, totalPulses]
