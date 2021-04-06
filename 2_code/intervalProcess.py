import multiprocessing as mp
import numpy as np
import math
import common
import time
import logging
from columnar import columnar
import util

class cInterval:
    intervals_total: int = 0
    interval_current_Tstart: float = 0
    interval_current_Tstop: float = 0
    coincidence_profile = None
    pulse_profile = None
    jammer_profile = None

    def __init__(self, numIntervalLength_ms, numFlightTime_ms):
        self.intervals_total = intervalsInFlight(numIntervalLength_ms, numFlightTime_ms)

class cCoincidence:
    radar_id: int = 0
    pulse_number: int = 0
    coincidence_number: int = 0

    def __init__(self, numRadar_id, numPulse_number, numCoincidence_idx):
        self.radar_id = numRadar_id
        self.pulse_number = numPulse_number
        self.coincidence_number = numCoincidence_idx

class cTIJ:
    radar_id: int = 0
    za: float = 0
    ma: float = 0
    jpp: float = 0

    def __init__(self, numRadar_ID):
        self.radar_id = numRadar_ID

def intervalsInFlight(numIntervalLength_ms, numFlightTime_ms):
    '''
    intervalsInFlight

    calculate the number of constant intervals during a flight

    Parameters
    ----------
    numIntervalLength_ms : [float]
        The time lenght in milliseconds of the interval
    numFlightTime_ms : [float]
        The total flight time of the platform in milliseconds

    Returns
    -------
    [int]
        The total number of intervals during the entire flight.
        NOTE for this iteration the intervals will be constant
        TODO: dynamic intervals?
    '''
    return math.ceil(numFlightTime_ms/numIntervalLength_ms)

def intervalProcessor(oPlatform, oJammer, olThreats, olChannels):
    '''
    intervalProcessor

    This function gets called at the start of an interval to perform ESM

    Parameters
    ----------
    oPlatform : [cPlatform object]
        [description]
    oJammer : [cJammer object]
        [description]
    olThreats : [cThreats object list]
        [description]
    olChannels : [cJammer cChannel object list]
        [description]
    '''

    sortThreatsTolChannels(olThreats, olChannels)

    lThreatTij = util.init_seperate_list_of_objects(olChannels.__len__())

    [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat] = intervalCoincidenceCalculator(olChannels)

    for chanIdx, chanItem in enumerate(olChannels):
        for threatIdx, threatItem in enumerate(chanItem.oThreatLib):
            threatItem.lIntervalPulseStore = lThreatPulseLib[chanIdx][threatIdx]
            threatItem.lIntervalPulseCoincidenceStore = lAllCoincidencePerThreat[chanIdx][threatIdx]
            threatItem.lIntervalTIJStore = cTIJ(threatItem.radar_id)

    cpiSweeper(olChannels,lCoincidenceLib)

    pass

def sortThreatsTolChannels(olThreats, olChannels):
    '''
    sortThreatsTolChannels

    At the start of a new interval sort the threats to the corresponding.
    The threat modes may have changed during OECM. The new mode/emitter signal characteristics will then
    be different requiring the ESM operations to place it in a new jamming channel

    Parameters
    ----------
    olThreats : [cThreats object list]
        [description]
    olChannels : [cJammer cChannel object list]
        [description]
    '''
    # clear the channel threats
    clearChannelThreats(olChannels)
    # check the current/changed threat freq and place into right freq channel
    for threatItem in olThreats:
        if (threatItem.emitter_current.__len__() > 0):
            for chanItem in olChannels:
                if (threatItem.emitter_current[common.THREAT_FREQ] >= chanItem.channel_range_MHz[0] and threatItem.emitter_current[common.THREAT_FREQ] <= chanItem.channel_range_MHz[1]):
                    chanItem.oThreatLib.append(threatItem)
                    break

def clearChannelThreats(olChannels):
    '''
    clearChannelThreats

    clears the threat library for each channel at the start of a new interval

    Parameters
    ----------
    olChannels : [cJammer cChannel object list]
        [description]
    '''
    for chanItem in olChannels:
        chanItem.oThreatLib = []

def intervalCoincidenceCalculator(olChannels):
    '''
    intervalCoincidenceCalculator

    Calculate all of the coincidences that occurs in each of the channel intervals

    Parameters
    ----------
    olChannels : [cJammer cChannel object list]
        [description]
    '''
    lCoincidenceLib = [None]*olChannels.__len__()
    lThreatPulseLib = [None]*olChannels.__len__()
    lAllCoincidencePerThreat = [[]]*olChannels.__len__()

    retList = [None]*3 # [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat]
    idx = 0
    coincIdx = 0
    timeCounter = [0]*2 # start and stop
    loggingCoincHeader = ['Threat ID', 'Pulses', 'Coincidence', 'c/p [%]', 'PRI [us]', 'PW [us]', 'Duty Cycle [%]']
    loggingCoincData = []

    for idx, chanItem in enumerate(olChannels):
        lThreatPulseLib[idx] = np.zeros((chanItem.oThreatLib.__len__(), common.INTERVAL_LIB_SIZE))
        for idy, threatItem in enumerate(chanItem.oThreatLib):
            initlThreatPulseLib(lThreatPulseLib[idx], idy, threatItem, chanItem.oecm_time_ms)

    timeCounter[0] = time.perf_counter()
    logging.info("Number of processors: %s", mp.Pool(mp.cpu_count()))
    retList = mp.Pool(olChannels.__len__()).map(pulseCoincidenceAssessor, lThreatPulseLib)

    for coincIdx in range(olChannels.__len__()):
        lCoincidenceLib[coincIdx] = retList[coincIdx][1]
        lThreatPulseLib[coincIdx] = retList[coincIdx][0]
        lAllCoincidencePerThreat[coincIdx] = np.array(retList[coincIdx][2])

        logging.debug("Channel %d stats:\ttotal coincidences: %d\n", coincIdx, lCoincidenceLib[coincIdx].__len__())

        lThreatPulseLib[coincIdx][:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = lThreatPulseLib[coincIdx][:, common.INTERVAL_LIB_COINCIDENCE_NUMBER] / lThreatPulseLib[coincIdx][:, common.INTERVAL_LIB_PULSE_NUMBER]

        loggingCoincData = []
        for logIdx in range(0, lThreatPulseLib[coincIdx].__len__()):
            loggingCoincData.append(
            [lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_RADAR_ID], lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PULSE_NUMBER], lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER], lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_INTERVAL_COINCIDENCE_PERC]*100, lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PRI_US], lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PW_US], lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PW_US]/lThreatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PRI_US]*100])

        table = columnar(loggingCoincData, loggingCoincHeader, no_borders=True)
        logging.debug("\n\n"+table+"\n\n")

    timeCounter[1] = time.perf_counter()
    logging.debug( "%s seconds to complete coincidence assessor for interval", timeCounter[1] - timeCounter[0] )

    return [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat]

def initlThreatPulseLib(lThreatPulseLib, index, threatItem, jammingIntervalTime_ms):
    '''
    initlThreatPulseLib

    Update the threat pulse library for coincidence calculation

    Parameters
    ----------
    lThreatPulseLib : [type]
        [description]
    threatItem : [type]
        [description]
    '''

    lThreatPulseLib[index, common.INTERVAL_LIB_RADAR_ID] = threatItem.radar_id # threat id
    lThreatPulseLib[index, common.INTERVAL_LIB_PULSE_START] = 0 # pulse start
    lThreatPulseLib[index, common.INTERVAL_LIB_PULSE_STOP] = 0 # pulse end
    lThreatPulseLib[index, common.INTERVAL_LIB_PRI_US] = threatItem.emitter_current[common.THREAT_PRI] # pri
    lThreatPulseLib[index, common.INTERVAL_LIB_PW_US] = threatItem.emitter_current[common.THREAT_PW] # pw
    lThreatPulseLib[index, common.INTERVAL_LIB_PULSE_NUMBER] = 1 # current pulse number/total pulses
    lThreatPulseLib[index, common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0 # total coincidence
    lThreatPulseLib[index, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = 0 # pulse coincidence/total pulses in interval perc
    lThreatPulseLib[index, common.INTERVAL_LIB_OECM_TIME_US] = jammingIntervalTime_ms * 1000 # oecm timein us

def pulseCoincidenceAssessor(sarrThreats):
    '''
    pulseCoincidenceAssessor

    calculate each channels coinicidence using parralel processing

    Parameters
    ----------
    sarrThreats : [type]
        [description]
    '''
    Tend = 0.0 # Farthest Tend
    Tstart = 0.0
    TRadarIdx = None
    lTcoincidenceIdx = None
    inCoincidence = False
    lcoincidence = []
    lAllCoincidencePerThreat = util.init_seperate_list_of_objects(sarrThreats.__len__())
    retList = [None]*3 # [sarrThreats, lcoincidence, lAllCoincidencePerThreat]

    # update times and increase pulse total
    for idx in range(sarrThreats.__len__()):
        sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] =  sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] + sarrThreats[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW

    # loop over entire interval duration
    while(Tend <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US] or Tstart <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US]):
        # 1. get the first pulse
        TRadarIdx = np.max(np.where(sarrThreats[:, common.INTERVAL_LIB_PULSE_START] == np.min(sarrThreats[:, common.INTERVAL_LIB_PULSE_START])))
        # 3. Tend > Tstart: coincidence check Tend with all of the next lowest Tstart pulses
        lTcoincidenceIdx = np.where(np.logical_and((sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_STOP] >= sarrThreats[:, common.INTERVAL_LIB_PULSE_START]),(sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_START] <= sarrThreats[:, common.INTERVAL_LIB_PULSE_START]) ) )

        if(len(lTcoincidenceIdx[0]) == 1):
            if(inCoincidence == True):
                sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
                for coincRadarIdx in np.nditer(lTcoincidenceIdx[0]):
                    lcoincidence[-1].append(cCoincidence(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_RADAR_ID],
                                                         sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                                         sarrThreats[coincRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]) )
                    lAllCoincidencePerThreat[coincRadarIdx].append(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER])
            inCoincidence = False
        else:
            # 5. check to find the highest Tend of the coincidence pulses
            TRadarIdx = np.max(np.where(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] == np.max(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP])))
            lTcoincidenceIdx = np.delete(lTcoincidenceIdx[0], TRadarIdx)
            sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
            lTempCoinc = []

            for coincRadarIdx in np.nditer(lTcoincidenceIdx[0]):
                lTempCoinc.append(cCoincidence(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_RADAR_ID],
                                               sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                               sarrThreats[coincRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]) )
                lAllCoincidencePerThreat[coincRadarIdx].append(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER])
            if(inCoincidence == True):
                lcoincidence[-1].extend(lTempCoinc)
            else:
                lcoincidence.append(lTempCoinc)

            inCoincidence = True

        # 6. update all of the pulses Tstart
        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PRI_US]

        # 7. update all of the pulses Tend
        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] + sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PW_US]

        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1

        Tend = sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_STOP]
        Tstart = sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_START]

    retList[0] = sarrThreats
    retList[1] = lcoincidence
    retList[2] = lAllCoincidencePerThreat

    return retList

def cpiSweeper(olChannels,lCoincidenceLib):
    pass