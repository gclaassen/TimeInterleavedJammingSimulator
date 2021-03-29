import multiprocessing as mp
import numpy as np
import math
import common

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
    threatPulseLib = [None]*olChannels.__len__()
    for idx, chanItem in enumerate(olChannels):
        threatPulseLib[idx] = np.zeros((chanItem.oThreatLib.__len__(), common.INTERVAL_LIB_SIZE))
        for idy, threatItem in enumerate(chanItem.oThreatLib):
            initThreatPulseLib(threatPulseLib[idx], idy, threatItem, chanItem.oecm_time_ms)


    print("Number of processors: ", mp.Pool(mp.cpu_count()))
    [threatPulseLib] = mp.Pool().map(pulseCoincidence, threatPulseLib)
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
    threatPulseLib[index, common.INTERVAL_LIB_PULSE_NUMBER] = 0 # current pulse number/total pulses
    threatPulseLib[index, common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0 # total coincidence
    threatPulseLib[index, common.INTERVAL_LIB_OECM_TIME_US] = jammingIntervalTime_ms * 1000 # oecm timein us

def pulseCoincidence(sarrThreats):
    '''
    pulseCoincidence

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

#TODO: check if coincidence calc work and create arr
    # update times and increase pulse total
    for idx in range(sarrThreats.__len__()):
        sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI
        sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] + sarrThreats[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW
        # sarrThreats[idx, common.INTERVAL_LIB_PULSE_NUMBER] += 1 # count pulse

    # loop over entire interval duration
    while(Tend <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US] or Tstart <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US]):
        # 1. get the first pulse
        TRadarIdx = np.max(np.where(sarrThreats[:, common.INTERVAL_LIB_PULSE_START] == np.min(sarrThreats[:, common.INTERVAL_LIB_PULSE_START])))
        # 3. Tend > Tstart: coincidence check Tend with all of the next lowest Tstart pulses
        lTcoincidenceIdx = np.where(np.logical_and((sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_STOP] >= sarrThreats[:, common.INTERVAL_LIB_PULSE_START]), (sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_START] <= sarrThreats[:, common.INTERVAL_LIB_PULSE_START])) )

        if(len(lTcoincidenceIdx[0]) == 1):
            inCoincidence = False
        else:
            inCoincidence = True
            sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
            # 5. check to find the highest Tend of the coincidence pulses
            TRadarIdx = np.max(np.where(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] == np.max(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP])))
            lTcoincidenceIdx = np.delete(lTcoincidenceIdx[0], TRadarIdx)

        # 6. update all of the pulses Tstart
        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PRI_US]

        # 7. update all of the pulses Tend
        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] + sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PW_US]

        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1

        Tend = sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_STOP]
        Tstart = sarrThreats[TRadarIdx, common.INTERVAL_LIB_PULSE_START]
        
    return sarrThreats