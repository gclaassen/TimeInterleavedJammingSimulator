from numba import cuda
import numpy
import math
import common

class cInterval:
    intervals_total: int = 0
    interval_current_Tstart: float = 0
    interval_current_Tstop: float = 0
    coincidence_profile = None
    pulse_profile = None
    jammer_profile = None

class cCoincidence:
    radar_id: int = 0
    pulse_number: int = 0

    def __init__(self, numIntervalLength_ms, numFlightTime_ms):
        self.intervals_total = intervalsInFlight(numIntervalLength_ms, numFlightTime_ms)

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

def intervalEsmProcessor(oPlatform, oJammer, oThreats, oChannels):
    '''
    intervalEsmProcessor

    This function gets called at the start of an interval to perform ESM

    Parameters
    ----------
    oPlatform : [cPlatform object]
        [description]
    oJammer : [cJammer object]
        [description]
    oThreats : [cThreats object list]
        [description]
    oChannels : [cJammer cChannel object list]
        [description]
    '''
    sortThreatsToChannels(oThreats, oChannels)
    intervalCoincidenceCalculator(oChannels)
    pass

def sortThreatsToChannels(oThreats, oChannels):
    '''
    sortThreatsToChannels

    At the start of a new interval sort the threats to the corresponding.
    The threat modes may have changed during OECM. The new mode/emitter signal characteristics will then
    be different requiring the ESM operations to place it in a new jamming channel

    Parameters
    ----------
    oThreats : [cThreats object list]
        [description]
    oChannels : [cJammer cChannel object list]
        [description]
    '''
    # clear the channel threats
    clearChannelThreats(oChannels)
    # check the current/changed threat freq and place into right freq channel
    for threatItem in oThreats:
        if (threatItem.emitter_current != None):
            for chanItem in oChannels:
                if (threatItem.emitter_current[common.THREAT_FREQ] >= chanItem.channel_range_MHz[0] and threatItem.emitter_current[common.THREAT_FREQ] <= chanItem.channel_range_MHz[1]):
                    chanItem.oThreatLib.append(threatItem)
                    break

def clearChannelThreats(oChannels):
    '''
    clearChannelThreats

    clears the threat library for each channel at the start of a new interval

    Parameters
    ----------
    oChannels : [cJammer cChannel object list]
        [description]
    '''
    for chanItem in oChannels:
        chanItem.oThreatLib = []

def intervalCoincidenceCalculator(oChannels):
    pass