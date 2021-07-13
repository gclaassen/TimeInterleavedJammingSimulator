import numpy as np
import common
import math
import mathRadar as radarmath
import logging
import util

class cThreat:
    # Radar Parameters
    m_radar_id: int = 0
    m_radar_name = None
    m_location: None
    m_emitters = None
    m_cpiStart = 0

    # Weapon System
    m_lethalRange_km = 0

    # current mode parameters
    m_start_mode = NotImplementedError
    m_emitter_current = None
    m_mode_current_ID = None
    m_mode_current_Name = None
    m_channel_current = None

    #interval Info
    oThreatPulseLib = np.zeros(common.INTERVAL_LIB_SIZE)
    oIntervalTIJStore = None
    lIntervalCoincidences = None
    lIntervalModeChangeLog = None
    lIntervalCoincidencePercentageLog = None
    lIntervalZoneAssessmentLog = None
    lIntervalLethalRangeLog = None
    lIntervalJammingLog = None
    lDetectionsInIntervalLog = None
    lModesForEmitter = []
    m_firstIntervalForMode = True

    # platform detected
    lCpiDetect = []
    
    def __init__(self, threatList):
        emitterSize = None

        self.m_radar_id = threatList[common.THREAT_ID]
        self.m_radar_name = threatList[common.THREAT_NAME]
        self.m_lethalRange_km = threatList[common.THREAT_LETHAL_RANGE_KM]
        self.m_start_mode = threatList[common.THREAT_START_MODE]
        logging.debug("Threat: %s id: %s",self.m_radar_name, self.m_radar_id)
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
        self.m_emitters = convertEmitterJsonToArray(
            threatList[common.THREAT_EMITTERS], emitterSize)

        if(self.m_emitters.__len__() > 0):
            self.lModesForEmitter = listAllModesInEmitter(self.m_emitters[0][:])
            #TODO: currently only cater so a single emitter with single or multiple different modes
            ##TODO: where does the modes for the emitter start -> min, max, varied
            startMode = self.m_start_mode
            self.m_mode_current_ID = startMode
            self.m_emitter_current = self.m_emitters[0][self.lModesForEmitter.index(startMode)]
            self.m_mode_current_Name = common.dictModes[self.m_mode_current_ID]

def listAllModesInEmitter(emitterObject):
    lModesForEmitter = []
    for mode in emitterObject:
        lModesForEmitter.append(mode[common.THREAT_MODE_ID])

    return lModesForEmitter

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
                                            (common.THREAT_EMITTER_NOISEFIGURE_DB,float),
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
                                            (common.THREAT_CPI_AT_INTERVAL, int),
                                            (common.THREAT_PROB_DETECTION, float),
                                            (common.THREAT_PROB_FALSE_ALARM, float),
                                            (common.THREAT_PROB_DETECTION_MIN, float),
                                            (common.THREAT_PROB_DETECTION_CUMULATIVE, int)
                                        ], order='C')
        for modeIndex in range(0, modeSize):

            if(isMultipleModes == True):
                modeNode = emitterNode[common.THREAT_MODES][modeIndex]
            else:
                modeNode = emitterNode[common.THREAT_MODES]

            emitters[emmiterIndex][modeIndex][common.THREAT_EMITTER_ID] = emitterNode[common.THREAT_EMITTER_ID]
            emitters[emmiterIndex][modeIndex][common.THREAT_EMITTER_NOISEFIGURE_DB] = emitterNode[common.THREAT_EMITTER_NOISEFIGURE_DB]
            emitters[emmiterIndex][modeIndex][common.THREAT_MODE_ID] = modeNode[common.THREAT_MODE_ID]
            emitters[emmiterIndex][modeIndex][common.THREAT_MODE_TYPE] = modeNode[common.THREAT_MODE_TYPE]
            emitters[emmiterIndex][modeIndex][common.THREAT_PEAKPOWER_KW] = modeNode[common.THREAT_PEAKPOWER_KW]
            emitters[emmiterIndex][modeIndex][common.THREAT_GAIN] = modeNode[common.THREAT_GAIN]
            emitters[emmiterIndex][modeIndex][common.THREAT_FREQ_MHZ] = modeNode[common.THREAT_FREQ_MHZ]
            emitters[emmiterIndex][modeIndex][common.THREAT_PRI_US] = modeNode[common.THREAT_PRI_US]
            emitters[emmiterIndex][modeIndex][common.THREAT_PW_US] = modeNode[common.THREAT_PW_US]
            emitters[emmiterIndex][modeIndex][common.THREAT_DUTY_CYCLE] = radarmath.calculateDutyCycle(modeNode[common.THREAT_PW_US], modeNode[common.THREAT_PRI_US])
            emitters[emmiterIndex][modeIndex][common.THREAT_CPI] = modeNode[common.THREAT_CPI]
            emitters[emmiterIndex][modeIndex][common.THREAT_CPI_AT_INTERVAL] = modeNode[common.THREAT_CPI_AT_INTERVAL]
            emitters[emmiterIndex][modeIndex][common.THREAT_AVGPOWER_KW] = radarmath.convertPeakPowerToAvgPower(emitters[emmiterIndex][modeIndex][common.THREAT_PEAKPOWER_KW], emitters[emmiterIndex][modeIndex][common.THREAT_DUTY_CYCLE])
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_DETECTION] = modeNode[common.THREAT_PROB_DETECTION]
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_FALSE_ALARM] = modeNode[common.THREAT_PROB_FALSE_ALARM]
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_DETECTION_MIN] = modeNode[common.THREAT_PROB_DETECTION_MIN]
            emitters[emmiterIndex][modeIndex][common.THREAT_PROB_DETECTION_CUMULATIVE] = modeNode[common.THREAT_PROB_DETECTION_CUMULATIVE]
    return emitters


def convertThreatJsonToClass(jsonThreatDict):
    jsonThreatList = jsonThreatDict[common.THREAT_THREATS]
    threatClass = util.initSeparateListOfObjects(jsonThreatList.__len__())

    for idx, jsonThreat in enumerate(jsonThreatList):
        threatClass[idx] = cThreat(jsonThreat)

    return threatClass

def PriTimeRange(Tstart_ns, Tstop_ns, PRI):
    PriStart = [(Tstart_ns//PRI)*PRI] + PRI
    PriStop = [(Tstop_ns//PRI)*PRI] + PRI
    totalPulses = math.ceil((PriStop - PriStart)/PRI)

    return [PriStart, PriStop, totalPulses]

def initListThreatPulseLib(threatItem, jammer):
    threatPulseLib = np.zeros(common.INTERVAL_LIB_SIZE)
    threatPulseLib[common.INTERVAL_LIB_RADAR_ID] = threatItem.m_radar_id # threat id
    threatPulseLib[common.INTERVAL_LIB_PULSE_START] = 0 # pulse start
    threatPulseLib[common.INTERVAL_LIB_PULSE_STOP] = 0 # pulse end
    threatPulseLib[common.INTERVAL_LIB_NOISE_PULSE_START] = 0 # pulse start
    threatPulseLib[common.INTERVAL_LIB_NOISE_PULSE_STOP] = 0 # pulse end
    threatPulseLib[common.INTERVAL_LIB_PRI_US] = threatItem.m_emitter_current[common.THREAT_PRI_US] # pri
    threatPulseLib[common.INTERVAL_LIB_PW_US] = threatItem.m_emitter_current[common.THREAT_PW_US] # pw
    if common.ARG_JAMMINGBINPRI: # TODO: move to seperate function as this is called twice
            if jammer.jammer_bin_size_pri == 0:
                jammingBound_us = 0
            else:
                jammingEnvelope = threatPulseLib[common.INTERVAL_LIB_PRI_US] * jammer.jammer_bin_size_pri
                jammingBound_us = (jammingEnvelope)/2 if jammingEnvelope > threatPulseLib[common.INTERVAL_LIB_PW_US] else threatPulseLib[common.INTERVAL_LIB_PW_US]*0.75
                threatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - threatPulseLib[common.INTERVAL_LIB_PW_US]/2
    else:
        if common.ARG_CUTPULSEATEND:
            jammingEnvelopeStart = threatPulseLib[common.INTERVAL_LIB_PW_US] * jammer.jammer_bin_size_pw
            jammingBound_us = (jammingEnvelopeStart)/2
            jammingEnvelopStop = threatPulseLib[common.INTERVAL_LIB_PW_US] * 0.05 # cover pulse fall time is 5% of pulse width
            threatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = jammingBound_us
            threatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingEnvelopStop - threatPulseLib[common.INTERVAL_LIB_PW_US]/2
        else:
            if jammer.jammer_bin_size_pw == 0:
                jammingBound_us = 0
                threatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - threatPulseLib[common.INTERVAL_LIB_PW_US]/2
            else:
                jammingEnvelope = threatPulseLib[common.INTERVAL_LIB_PW_US] * jammer.jammer_bin_size_pw
                jammingBound_us = (jammingEnvelope)/2
                threatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - threatPulseLib[common.INTERVAL_LIB_PW_US]/2
    threatPulseLib[common.INTERVAL_LIB_PULSE_NUMBER] = 1 # current pulse number/total pulses
    threatPulseLib[common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0 # total coincidence
    threatPulseLib[common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = 0 # pulse coincidence/total pulses in interval perc
    threatPulseLib[common.INTERVAL_STOP_TIME_US] = 0# interval end time in us

    return threatPulseLib

