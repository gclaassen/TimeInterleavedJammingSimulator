import multiprocessing as mp
import numpy as np
import math
import common
import time
import logging

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

def intervalEsmProcessor(oPlatform, oJammer, olThreats, olChannels):
    '''
    intervalEsmProcessor

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
    intervalCoincidenceCalculator(olChannels)
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
    threatPulseLib = [None]*olChannels.__len__()
    retList = [None]*2 # [threatPulseLib, lCoincidenceLib]
    idx = 0
    coincIdx = 0
    timeCounter = [0]*2 # start and stop

    for idx, chanItem in enumerate(olChannels):
        threatPulseLib[idx] = np.zeros((chanItem.oThreatLib.__len__(), common.INTERVAL_LIB_SIZE))
        for idy, threatItem in enumerate(chanItem.oThreatLib):
            initThreatPulseLib(threatPulseLib[idx], idy, threatItem, chanItem.oecm_time_ms)

    timeCounter[0] = time.perf_counter()
    logging.info("Number of processors: %s", mp.Pool(mp.cpu_count()))
    retList = mp.Pool(olChannels.__len__()).map(pulseCoincidenceAssessor, threatPulseLib)

    for coincIdx in range(olChannels.__len__()):
        lCoincidenceLib[coincIdx] = retList[coincIdx][1]
        threatPulseLib[coincIdx] = retList[coincIdx][0]
        threatPulseLib[coincIdx][:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = threatPulseLib[coincIdx][:, common.INTERVAL_LIB_COINCIDENCE_NUMBER] / threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PULSE_NUMBER]

        # for logIdx in range(0, np.size(threatPulseLib[coincIdx])):
            # logging.debug("#T%s \t[id: %s]  \t[pulses: %s] \t[coincidence: %s \t[c/p: %s] \t[PRI %sus] \t[PW: %sus]", logIdx, threatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_RADAR_ID], threatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PULSE_NUMBER], threatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER], threatPulseLib[coincIdx][logIdx, common.INTERVAL_INTERVAL_COINCIDENCE_PERC], threatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PRI_US], threatPulseLib[coincIdx][logIdx, common.INTERVAL_LIB_PW_US])

        logging.debug("[id: %d] \t[pulses: %d] \t[coincidence: %d] \t[c/p: %.3f] \t[PRI %fus] \t[PW: %fus] \t[Duty Cycle: %f]", threatPulseLib[coincIdx][:, common.INTERVAL_LIB_RADAR_ID], threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PULSE_NUMBER], threatPulseLib[coincIdx][:, common.INTERVAL_LIB_COINCIDENCE_NUMBER], threatPulseLib[coincIdx][:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC], threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PRI_US], threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PW_US], threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PW_US]/threatPulseLib[coincIdx][:, common.INTERVAL_LIB_PRI_US] )

    timeCounter[1] = time.perf_counter()
    logging.debug("%s seconds to complete coincidence assessor for interval", timeCounter[1]-timeCounter[0])
    
    pass

def initThreatPulseLib(threatPulseLib, index, threatItem, jammingIntervalTime_ms):
    '''
    initThreatPulseLib

    Update the threat pulse library for coincidence calculation

    Parameters
    ----------
    threatPulseLib : [type]
        [description]
    threatItem : [type]
        [description]
    '''
    
    threatPulseLib[index, common.INTERVAL_LIB_RADAR_ID] = threatItem.radar_id # threat id
    threatPulseLib[index, common.INTERVAL_LIB_PULSE_START] = 0 # pulse start
    threatPulseLib[index, common.INTERVAL_LIB_PULSE_STOP] = 0 # pulse end
    threatPulseLib[index, common.INTERVAL_LIB_PRI_US] = threatItem.emitter_current[common.THREAT_PRI] # pri
    threatPulseLib[index, common.INTERVAL_LIB_PW_US] = threatItem.emitter_current[common.THREAT_PW] # pw
    threatPulseLib[index, common.INTERVAL_LIB_PULSE_NUMBER] = 1 # current pulse number/total pulses
    threatPulseLib[index, common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0 # total coincidence
    threatPulseLib[index, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = 0 # pulse coincidence/total pulses in interval perc
    threatPulseLib[index, common.INTERVAL_LIB_OECM_TIME_US] = jammingIntervalTime_ms * 1000 # oecm timein us

def pulseCoincidenceAssessor(sarrThreats):
    '''
    pulseCoincidenceAssessor

    calculate each channels coinicidence using parralel processing

    Parameters
    ----------
    sarrThreats : [type]
        [description]
    '''
    Tend = 0.0 #Farthest Tend
    Tstart = 0.0
    TRadarIdx = None
    lTcoincidenceIdx = None
    inCoincidence = False
    lcoincidence = []
    retList = [None]*2

#TODO: problem with coinc with more than 2 pulses. keep same array when still in coincidence for next round
    # update times and increase pulse total
    for idx in range(sarrThreats.__len__()):
        sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] =  sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] + sarrThreats[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW
        # sarrThreats[idx, common.INTERVAL_LIB_PULSE_NUMBER] += 1 # count pulse

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

    return retList