import multiprocessing as mp
import numpy as np
import math
import common
import time
import logging
from tabulate import tabulate
import util
# from tqdm import tqdm
from dataclasses import dataclass, astuple, asdict
import tijZA as za
import tijMA as ma
import tijTR as tr
import mathRadar as radmath

class cInterval:
    intervals_total: int = 0
    interval_current: int = 0
    interval_length_us: float = 0
    interval_current_Tstart_us: float = 0
    interval_current_Tstop_us: float = 0
    flightTime_us: float = 0

    def __init__(self, numIntervalLength_us, numFlightTime_us):
        self.intervals_total = intervalsInFlight(numIntervalLength_us, numFlightTime_us)
        self.interval_length_us = numIntervalLength_us
        self.flightTime_us = numFlightTime_us

@dataclass(frozen=True, order=True)
class cCoincidence:
    radar_idx: int = 0
    radar_id: int = 0
    pulse_number: int = 0
    coincidence_number: int = 0
    timeOfCoincidence_us: float = 0


class cTIJ:
    radar_id: int = 0

    # za
    za: float = 0
    platformDistance_km: float = 0.0
    maxRadarRange_km: float = 0.0
    burnthroughRange_km: float = 0.0

    # ma
    ma: float = 0

    # JPP
    jpp: float = 0
    jpp_req: float = 0
    jpp_dif: float = 0

    cpi: float = 0
    cpi_startAt: int = 0

    Pd_req: float = 0
    Pd_startAt: float = 0
    SNR_startAt: float = 0

    def __init__(self, numRadar_ID, numCPI, numJPP_req):
        self.radar_id = numRadar_ID
        self.cpi = numCPI
        self.jpp_req = numJPP_req

def intervalsInFlight(numIntervalLength_us, numFlightTime_us):
    '''
    intervalsInFlight

    calculate the number of constant intervals during a flight

    Parameters
    ----------
    numIntervalLength_us : [float]
        The time lenght in milliseconds of the interval
    numFlightTime_us : [float]
        The total flight time of the platform in milliseconds

    Returns
    -------
    [int]
        The total number of intervals during the entire flight.
        NOTE for this iteration the intervals will be constant
        TODO: dynamic intervals?
    '''
    return math.ceil(numFlightTime_us/numIntervalLength_us)

def intervalProcessor(oPlatform, oJammer, olThreats, oChannel):
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
    oChannel : [cJammer cChannel object list]
        [description]
    '''

    loggingRangeHeader = ['Threat ID', 'Interval Start Time [us]', 'Radar to Platform Distance [km]']
    loggingRangeData = []

    for intervalIdx in range(0, oChannel.oInterval.intervals_total):
        logging.info("\nInterval %s of %s\n", intervalIdx+1, oChannel.oInterval.intervals_total)

        oChannel.oInterval.interval_current = intervalIdx
        oChannel.oInterval.interval_current_Tstart = oChannel.interval_time_us * intervalIdx
        if((intervalIdx + 1) == oChannel.oInterval.intervals_total):
            oChannel.oInterval.interval_current_Tstop_us = oPlatform.timeStop_us
        else:
            oChannel.oInterval.interval_current_Tstop_us = oChannel.oInterval.interval_current_Tstart + oJammer.oChannel[0].interval_time_us

        # Get the starting ranges at each new interval
        loggingRangeData = []
        for threatIdx, threatItem in enumerate(olThreats):
            RadarDistance_km = za.calculateplatformDistance_km(oChannel.oInterval.interval_current_Tstart, oPlatform.flightPath, threatItem.location)
            loggingRangeData.append([threatIdx+1, oChannel.oInterval.interval_current_Tstart, RadarDistance_km])

        table = tabulate(loggingRangeData, loggingRangeHeader, tablefmt="github")
        logging.debug( "\n\n"+table+"\n\n")

        sortThreatsToChannel(olThreats, oChannel) #TODO: what about mode changes
        [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat] = intervalCoincidenceCalculator(oChannel)

        oChannel.oCoincidences = lCoincidenceLib
        for threatIdx, threatItem in enumerate(oChannel.oThreatLib):
            threatItem.lIntervalPulseStore = lThreatPulseLib[threatIdx]
            threatItem.lIntervalPulseCoincidenceStore = lAllCoincidencePerThreat[threatIdx]
            threatItem.lIntervalTIJStore = cTIJ(threatItem.radar_id, threatItem.emitter_current[common.THREAT_CPI], threatItem.emitter_current[common.THREAT_PERCENTAGEJAMMING] )

        cpiSweeper(oChannel, oPlatform, oJammer)

    pass #TODO: remove

def sortThreatsToChannel(olThreats, oChannel):
    '''
    sortThreatsToChannel

    At the start of a new interval sort the threats to the corresponding.
    The threat modes may have changed during OECM. The new mode/emitter signal characteristics will then
    be different requiring the ESM operations to place it in a new jamming channel

    Parameters
    ----------
    olThreats : [cThreats object list]
        [description]
    oChannel : [cJammer cChannel object list]
        [description]
    '''
    # clear the channel threats
    oChannel.oThreatLib = []
    # check the current/changed threat freq and place into right freq channel
    for threatItem in olThreats:
        if (threatItem.emitter_current.__len__() > 0):
            if (threatItem.emitter_current[common.THREAT_FREQ_MHZ] >= oChannel.channel_range_MHz[0] and threatItem.emitter_current[common.THREAT_FREQ_MHZ] <= oChannel.channel_range_MHz[1]):
                oChannel.oThreatLib.append(threatItem)

def intervalCoincidenceCalculator(oChannel):
    '''
    intervalCoincidenceCalculator

    Calculate all of the coincidences that occurs in each of the channel intervals

    Parameters
    ----------
    oChannel : [cJammer cChannel object list]
        [description]
    '''
    lCoincidenceLib = [None]
    lThreatPulseLib = np.zeros((oChannel.oThreatLib.__len__(), common.INTERVAL_LIB_SIZE))
    lAllCoincidencePerThreat = [[]]

    retList = [None]*3 # [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat]
    timeCounter = [0]*2 # start and stop
    loggingCoincHeader = ['Threat ID', 'Pulses', 'Coincidence', 'c/p [%]', 'PRI [us]', 'PW [us]', 'Duty Cycle [%]']
    loggingCoincData = []

    for threatIdx, threatItem in enumerate(oChannel.oThreatLib):
        if(oChannel.oInterval.interval_current == 0):
            initlThreatPulseLib(lThreatPulseLib, threatIdx, threatItem, oChannel.oInterval.interval_length_us)
        else:
            lThreatPulseLib[threatIdx] = threatItem.lIntervalPulseStore
            lThreatPulseLib[threatIdx, common.INTERVAL_LIB_OECM_TIME_US] = oChannel.oInterval.interval_current_Tstart_us


    timeCounter[0] = time.perf_counter()
    retList = pulseCoincidenceAssessor(lThreatPulseLib)

    lCoincidenceLib = retList[1]
    lThreatPulseLib = retList[0]
    lAllCoincidencePerThreat = np.array(retList[2], dtype=object)

    logging.info("Stats:\ttotal coincidences: %d\n", lCoincidenceLib.__len__())

    lThreatPulseLib[:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = lThreatPulseLib[:, common.INTERVAL_LIB_COINCIDENCE_NUMBER] / lThreatPulseLib[:, common.INTERVAL_LIB_PULSE_NUMBER]

    loggingCoincData = []
    for logIdx in range(0, lThreatPulseLib.__len__()):
        loggingCoincData.append(
        [lThreatPulseLib[logIdx, common.INTERVAL_LIB_RADAR_ID], lThreatPulseLib[logIdx, common.INTERVAL_LIB_PULSE_NUMBER], lThreatPulseLib[logIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER], lThreatPulseLib[logIdx, common.INTERVAL_INTERVAL_COINCIDENCE_PERC]*100, lThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US], lThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US], lThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US]/lThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US]*100])

    table = tabulate(loggingCoincData, loggingCoincHeader, tablefmt="github")
    logging.debug( "\n\n"+table+"\n\n")

    timeCounter[1] = time.perf_counter()
    logging.info( "%s seconds to complete coincidence assessor for interval %s of size %s seconds", timeCounter[1] - timeCounter[0], oChannel.oInterval.interval_current, radmath.convertTime_MicrosecondsToMilliseconds(oChannel.oInterval.interval_length_us) )

    return [lThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat]

def initlThreatPulseLib(lThreatPulseLib, index, threatItem, jammingIntervalTime_us):
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
    lThreatPulseLib[index, common.INTERVAL_LIB_NOISE_PULSE_START] = 0 # pulse start
    lThreatPulseLib[index, common.INTERVAL_LIB_NOISE_PULSE_STOP] = 0 # pulse end
    lThreatPulseLib[index, common.INTERVAL_LIB_PRI_US] = threatItem.emitter_current[common.THREAT_PRI_US] # pri
    lThreatPulseLib[index, common.INTERVAL_LIB_PW_US] = threatItem.emitter_current[common.THREAT_PW_US] # pw
    lThreatPulseLib[index, common.INTERVAL_LIB_PULSE_NUMBER] = 1 # current pulse number/total pulses
    lThreatPulseLib[index, common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0 # total coincidence
    lThreatPulseLib[index, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = 0 # pulse coincidence/total pulses in interval perc
    lThreatPulseLib[index, common.INTERVAL_LIB_OECM_TIME_US] = jammingIntervalTime_us# oecm timein us

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
    # intervalBar = tqdm(total=sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US], unit='us')

    # update times and increase pulse total
    for idx in range(sarrThreats.__len__()):
        sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] =  sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] + sarrThreats[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW

        sarrThreats[idx, common.INTERVAL_LIB_NOISE_PULSE_START] = sarrThreats[idx, common.INTERVAL_LIB_PULSE_START] - sarrThreats[idx, common.INTERVAL_LIB_PW_US]*math.floor(common.JammingRangeBinSize/2) # shift start left for jamming bins
        sarrThreats[idx, common.INTERVAL_LIB_NOISE_PULSE_STOP]  = sarrThreats[idx, common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[idx, common.INTERVAL_LIB_PW_US]*math.floor(common.JammingRangeBinSize/2) # shift end right for jamming bins


    # loop over entire interval duration
    while(Tend <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US] or Tstart <= sarrThreats[0, common.INTERVAL_LIB_OECM_TIME_US]):
        # 1. get the first pulse
        TRadarIdx = np.max(np.where(sarrThreats[:, common.INTERVAL_LIB_NOISE_PULSE_START] == np.min(sarrThreats[:, common.INTERVAL_LIB_NOISE_PULSE_START])))
        # 3. Tend > Tstart: coincidence check Tend with all of the next lowest Tstart pulses
        lTcoincidenceIdx = np.where(np.logical_and((sarrThreats[TRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_STOP] >= sarrThreats[:, common.INTERVAL_LIB_NOISE_PULSE_START]),(sarrThreats[TRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START] <= sarrThreats[:, common.INTERVAL_LIB_NOISE_PULSE_START]) ) )

        if(len(lTcoincidenceIdx[0]) == 1):
            if(inCoincidence == True):
                sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
                for coincRadarIdx in np.nditer(lTcoincidenceIdx[0]):
                    lcoincidence[-1].append(cCoincidence(int(np.max(coincRadarIdx)),
                                                         int(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_RADAR_ID]),
                                                         sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                                         int(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]),
                                                         sarrThreats[coincRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START] ))
                    lAllCoincidencePerThreat[coincRadarIdx].append(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER])
            else:
                Tend = np.max(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP])
                Tstart = np.max(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START])
                # intervalBar.refresh()
                # intervalBar.update(Tend-intervalBar.last_print_n)
            inCoincidence = False
        else:
            # 5. check to find the highest Tend of the coincidence pulses
            TRadarIdx = np.max(np.where(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP] == np.max(sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP])))
            lTcoincidenceIdx = np.delete(lTcoincidenceIdx[0], TRadarIdx)
            sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
            lTempCoinc = []

            for coincRadarIdx in np.nditer(lTcoincidenceIdx[0]):
                lTempCoinc.append(cCoincidence(int(np.max(coincRadarIdx)),
                                               int(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_RADAR_ID]),
                                               sarrThreats[coincRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                               int(sarrThreats[coincRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]),
                                               sarrThreats[coincRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START]) )
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

        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START] = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] - sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PW_US]*math.floor(common.JammingRangeBinSize/2) # shift start left for jamming bins
        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP]  = sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PW_US]*math.floor(common.JammingRangeBinSize/2) # shift end right for jamming bins


        sarrThreats[lTcoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1


    retList[0] = sarrThreats
    retList[1] = lcoincidence
    retList[2] = lAllCoincidencePerThreat

    return retList

def cpiSweeper(oChannel, oPlatform, oJammer):

    threatList = oChannel.oThreatLib
    # coincBar = tqdm(total=chanItem.oCoincidences.__len__())
    loggingTijHeader = ['Coinc Pulse', 'Threat ID', 'Pp [kW]', 'Gtx [dBi]', 'Grx [dBi]', 'PW [us]', 'RCS [m^2]', 'Fc [MHz]', 'Ts [K]', 'Rc [km]', 'Lt [dB]', 'Ls [dB]', 'D0(x) [dB]', 'Pd', 'Pfa', 'CPI', '#Coinc CPI', 'JPP req', 'JPP curr', 'JPP diff', 'Rc [km]', 'Rm [km]', 'Rb [km]', 'ZA']
    loggingTijData = []


    for coincIdx, coincidence in enumerate(oChannel.oCoincidences):
        logging.debug("------------------------------------------------------------")
        logging.debug( "COINCIDENCE NUMBER: %d SIZE: %d", coincIdx, coincidence.__len__())
        logging.debug("------------------------------------------------------------")
        loggingTijData = []
        for coincPulseIdx, coincPulse in enumerate(coincidence):
            ##TODO: SNR and JSR calculations
            ##TODO: JPP - jamming pulse percentage
            radar_idx = coincPulse.radar_idx
            CoincidencesInCPI = np.where(np.logical_and(oChannel.oThreatLib[radar_idx].lIntervalPulseCoincidenceStore >= coincPulse.pulse_number, oChannel.oThreatLib[radar_idx].lIntervalPulseCoincidenceStore < (threatList[radar_idx].lIntervalTIJStore.cpi + coincPulse.pulse_number) ))

            # SNR and DETECTABILITY and INTEGRATION
            threatList[radar_idx].lIntervalTIJStore.platformDistance_km = za.calculateplatformDistance_km(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, threatList[radar_idx].location)

            SNR_D0 = radmath.radarEquation_DetectabilityFactor(
                threatList[radar_idx].emitter_current[common.THREAT_PEAKPOWER_KW],
                threatList[radar_idx].emitter_current[common.THREAT_GAIN],
                threatList[radar_idx].emitter_current[common.THREAT_GAIN],
                threatList[radar_idx].emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                threatList[radar_idx].emitter_current[common.THREAT_FREQ_MHZ],
                common.T0,
                threatList[radar_idx].lIntervalTIJStore.platformDistance_km,
                1, #TODO: determine losses
                1) #TODO: determine losses


            # TIJ - JAMMING PULSE PERCENTAGE
            threatList[radar_idx].lIntervalTIJStore.jpp = 1 - CoincidencesInCPI[0].__len__()/threatList[radar_idx].lIntervalTIJStore.cpi

            threatList[radar_idx].lIntervalTIJStore.jpp_dif = (threatList[radar_idx].lIntervalTIJStore.jpp_req - threatList[radar_idx].lIntervalTIJStore.jpp)/threatList[radar_idx].lIntervalTIJStore.jpp_req

            #TODO: TIJ - ZA
            [threatList[radar_idx].lIntervalTIJStore.platformDistance_km, threatList[radar_idx].lIntervalTIJStore.maxRadarRange_km, threatList[radar_idx].lIntervalTIJStore.burnthroughRange_km, threatList[radar_idx].lIntervalTIJStore.za] = za.calculateZoneAssessment(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, threatList[radar_idx].location)

            #TODO: TIJ - MA

            # logging.debug( "************************\n")

            loggingTijData.append(
            [
                coincPulseIdx+1,
                threatList[radar_idx].lIntervalTIJStore.radar_id,
                threatList[radar_idx].emitter_current[common.THREAT_PEAKPOWER_KW],
                threatList[radar_idx].emitter_current[common.THREAT_GAIN],
                threatList[radar_idx].emitter_current[common.THREAT_GAIN],
                threatList[radar_idx].emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                threatList[radar_idx].emitter_current[common.THREAT_FREQ_MHZ],
                common.T0,
                threatList[radar_idx].lIntervalTIJStore.platformDistance_km,
                1, #TODO: determine losses
                1,
                SNR_D0,
                threatList[radar_idx].emitter_current[common.THREAT_PROB_DETECTION],
                threatList[radar_idx].emitter_current[common.THREAT_PROB_FALSE_ALARM],
                threatList[radar_idx].lIntervalTIJStore.cpi,
                CoincidencesInCPI[0].__len__(),
                threatList[radar_idx].lIntervalTIJStore.jpp_req,
                threatList[radar_idx].lIntervalTIJStore.jpp,
                threatList[radar_idx].lIntervalTIJStore.jpp_dif,
                threatList[radar_idx].lIntervalTIJStore.platformDistance_km,
                threatList[radar_idx].lIntervalTIJStore.maxRadarRange_km,
                threatList[radar_idx].lIntervalTIJStore.burnthroughRange_km,
                threatList[radar_idx].lIntervalTIJStore.za
                ])

            #TODO: TIJ - TR

        table = tabulate(loggingTijData, loggingTijHeader, tablefmt="github")
        logging.debug( "\n\n"+table+"\n\n")

            #TODO: RADAR REAL

        # coincBar.update(1)
    #TODO: any radars not in coincidence?
    pass