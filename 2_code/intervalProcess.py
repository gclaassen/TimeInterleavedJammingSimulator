import multiprocessing as mp
import numpy as np
import math
import common
import time
import logging
from tabulate import tabulate
import util
from dataclasses import dataclass, astuple, asdict
import tijZA as za
import tijMA as ma
import tijTR as tr
import mathRadar as radarmath
from tqdm import tqdm
from numba import jit, cuda
import numba

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


def intervalsInFlight(numIntervalLength_us, numFlightTime_us):
    return math.ceil(numFlightTime_us/numIntervalLength_us)

def intervalProcessorSingleChannel(oPlatform, oJammer, olThreats, oChannel):

    lCoincidenceLib = []
    lAllCoincidencePerThreat = util.initSeparateListOfObjects(olThreats.__len__())

    __loggingRangeHeader = ['Threat ID', 'Interval Start Time [us]', 'Rc [km]', 'Rws [km]', 'Mode', 'Pp [kW]', 'Gtx [dBi]', 'Grx [dBi]', 'PW [us]', 'RCS [m^2]', 'Fc [MHz]', 'Ts [K]', 'CPI', 'Pfa', 'Pd', 'Pd jamming']
    __loggingRangeData = []

    __loggingJammerHeader = ['Pj [kW]', 'Gj [dB]', 'Bj [MHz]']
    __loggingJammerData = []


    __loggingJammerData.append([
                oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz])

    __loggingtable = tabulate(__loggingJammerData, __loggingJammerHeader, tablefmt="github")
    logging.debug( "\n\n"+ __loggingtable +"\n\n")

    oChannel.oInterval = cInterval(oChannel.oecm_time_us, oPlatform.timeStop_us)

    for __, threat in enumerate(olThreats):
        lTempIntervalLog = np.zeros(oChannel.oInterval.intervals_total+1)
        threat.lIntervalModeChangeLog = threat.lIntervalModeChangeLog + lTempIntervalLog

    for intervalIdx in range(0, oChannel.oInterval.intervals_total):
        logging.info("\nInterval %s of %s\n", intervalIdx+1, oChannel.oInterval.intervals_total)
        # print("Interval {0} of {1}".format(intervalIdx+1, oChannel.oInterval.intervals_total))

        oChannel.oInterval.interval_current = intervalIdx
        oChannel.oInterval.interval_current_Tstart_us = oChannel.interval_time_us * intervalIdx
        if((intervalIdx + 1) == oChannel.oInterval.intervals_total):
            oChannel.oInterval.interval_current_Tstop_us = oPlatform.timeStop_us
        else:
            oChannel.oInterval.interval_current_Tstop_us = oChannel.oInterval.interval_current_Tstart_us + oJammer.oChannel[0].interval_time_us

        # Get the starting ranges at each new interval
        __loggingRangeData = []
        for threatIdx, threatItem in enumerate(olThreats):
            RadarDistance_km = za.calculateplatformDistance_km(oChannel.oInterval.interval_current_Tstart_us, oPlatform.flightPath, threatItem.location)
            __loggingRangeData.append([
                threatIdx+1, 
                oChannel.oInterval.interval_current_Tstart_us, 
                RadarDistance_km, 
                threatItem.m_lethalRange_km,
                threatItem.m_mode_current_Name,
                threatItem.m_emitter_current[common.THREAT_PEAKPOWER_KW],
                threatItem.m_emitter_current[common.THREAT_GAIN],
                threatItem.m_emitter_current[common.THREAT_GAIN],
                threatItem.m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                threatItem.m_emitter_current[common.THREAT_FREQ_MHZ],
                common.T0,
                threatItem.m_emitter_current[common.THREAT_CPI],
                threatItem.m_emitter_current[common.THREAT_PROB_FALSE_ALARM],
                threatItem.m_emitter_current[common.THREAT_PROB_DETECTION],
                threatItem.m_emitter_current[common.THREAT_PROB_DETECTION_MIN],
                ])

        __loggingtable = tabulate(__loggingRangeData, __loggingRangeHeader, tablefmt="github")
        logging.debug( "\n\n"+ __loggingtable +"\n\n")

        updateThreatsForInterval(olThreats, oChannel, oJammer.jammer_bin_size) # TODO: for multiple channels

        intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat)

        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = np.asarray(lAllCoincidencePerThreat[threatIdx])
            threatItem.lIntervalJammingPulses = [] #TODO: add pulses selected for jamming

        coincidenceSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer)

        # TODO: review interval
        ## TODO: update radar
        threatEvaluation(intervalIdx, olThreats, oPlatform, oJammer)
        ## TODO: update jammer
        ## TODO: save interval data -> rerun purposes

        ## TODO: clear
        lCoincidenceLib = []
        lAllCoincidencePerThreat = util.initSeparateListOfObjects(olThreats.__len__())
        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = None
            threatItem.lIntervalJammingPulses = None

    logging.info("Post scenario stats:\n")
    for threat in enumerate(olThreats):
        logging.info("Threat Radar {0}: Mode Changes: {1}".format(threat.m_radar_id, threat.lModesForEmitter))

def updateThreatsForInterval(olThreats, oChannel, jammerEnvelopeSizeToPRI):
    for __, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib[common.INTERVAL_STOP_TIME_US] = oChannel.oInterval.interval_current_Tstop_us
        pri = threatItem.m_emitter_current[common.THREAT_PRI_US] # pri
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PRI_US] = pri
        pw = threatItem.m_emitter_current[common.THREAT_PW_US] # pw
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PW_US] = pw
        jammingEnvelope = pri*jammerEnvelopeSizeToPRI
        jammingBound_us = (jammingEnvelope-pw)/2 if jammingEnvelope > pw else 0
        threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_ENVELOPE] = jammingBound_us
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PULSE_NUMBER] = 1 # always start at pulse 1 otherwise if 0 we will get division by zero

def listOfThreatsInChannel(arrThreatPulseLib, olThreats, oChannel):
    for __, threatItem in enumerate(olThreats):
        arrThreatPulseLib.append(threatItem.oThreatPulseLib)

def moveThreatPulseLibToThreatObject(npArrThreatPulseLib, olThreats):
    for threatIdx, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib = npArrThreatPulseLib[threatIdx]

def intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat):

    # print("Determining coincidences...Please wait")
    arrThreatPulseLib = []

    timeCounter = [0]*2 # start and stop
    __loggingCoincidenceHeader = ['Threat ID', 'Pulses', 'PRI [us]', 'PW [us]', 'Duty Cycle [%]', 'Jamming Coincidences', 'c/p [%]', 'Jamming PW [us]', 'Jamming Duty Cycle [%]']
    __loggingCoincidenceData = []

    timeCounter[0] = time.perf_counter()

    listOfThreatsInChannel(arrThreatPulseLib, olThreats, oChannel)
    npArrThreatPulseLib = np.array(arrThreatPulseLib)

    pulseCoincidenceAssessor(npArrThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat)

    moveThreatPulseLibToThreatObject(npArrThreatPulseLib, olThreats)

    logging.info("Stats:\ttotal coincidences: %d\n", lCoincidenceLib.__len__())

    npArrThreatPulseLib[:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = npArrThreatPulseLib[:, common.INTERVAL_LIB_COINCIDENCE_NUMBER] / npArrThreatPulseLib[:, common.INTERVAL_LIB_PULSE_NUMBER]

    __loggingCoincidenceData = []
    for logIdx in range(0, npArrThreatPulseLib.__len__()):
        __loggingCoincidenceData.append([
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_RADAR_ID],
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PULSE_NUMBER],
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US],
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US],
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US]/npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US]*100,
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER],
            npArrThreatPulseLib[logIdx, common.INTERVAL_INTERVAL_COINCIDENCE_PERC]*100,
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_ENVELOPE]*2,
            (npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_ENVELOPE]*2)/npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US]*100])

    __loggingtable = tabulate(__loggingCoincidenceData, __loggingCoincidenceHeader, tablefmt="github")
    logging.debug( "\n\n"+ __loggingtable +"\n\n")

    timeCounter[1] = time.perf_counter()
    logging.info( "%s seconds to complete coincidence assessor for interval %s of size %s seconds", timeCounter[1] - timeCounter[0], oChannel.oInterval.interval_current, radarmath.convertTime_MicrosecondsToMilliseconds(oChannel.oInterval.interval_length_us) )

def pulseCoincidenceAssessor(npArrThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat):
    TRadarIdx = 0
    TCoincidenceIdx = 0
    inCoincidence = False

    # update times and increase pulse total
    for idx in range(npArrThreatPulseLib.__len__()):
        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW 

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] - (npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift start left for jamming bins

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + (npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift end right for jamming bins
    
    Tstart = np.min(npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START])
    Tend = np.min(npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START])

    TintervalStop = npArrThreatPulseLib[0 , common.INTERVAL_STOP_TIME_US]

    # loop over entire interval duration
    while(Tend <= TintervalStop or Tstart <= TintervalStop):
        # 1. get the first pulse
        TRadarIdx = np.max(np.where(npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START] == np.min(npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START])))
        # 3. Tend > Tstart: coincidence check Tend with all of the next lowest Tstart pulses
        TCoincidenceIdx = np.where(np.logical_and((npArrThreatPulseLib[TRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_STOP] >= npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START]),(npArrThreatPulseLib[TRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START] <= npArrThreatPulseLib[:, common.INTERVAL_LIB_NOISE_PULSE_START]) ) ) 

        if(len(TCoincidenceIdx[0]) == 1):
            if(inCoincidence == True):
                npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
                for coincidenceRadarIdx in np.nditer(TCoincidenceIdx[0]):
                    lCoincidenceLib[-1].append(cCoincidence(int(np.max(coincidenceRadarIdx)),
                                                         int(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_RADAR_ID]),
                                                         npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                                         int(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]),
                                                         npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START] ))
                    lAllCoincidencePerThreat[coincidenceRadarIdx].append(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER])
            else:
                Tend = np.max(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP])
                Tstart = np.max(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START])
                # intervalBar.refresh()
                # intervalBar.update(Tend-intervalBar.last_print_n)
            inCoincidence = False
        else:
            # 5. check to find the highest Tend of the coincidence pulses
            TRadarIdx = np.max(np.where(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP] == np.max(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP])))
            TCoincidenceIdx = np.delete(TCoincidenceIdx[0], TRadarIdx)
            npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_COINCIDENCE_NUMBER] += 1
            lTempCoinc = []

            for coincidenceRadarIdx in np.nditer(TCoincidenceIdx[0]):
                lTempCoinc.append(cCoincidence(int(np.max(coincidenceRadarIdx)),
                                               int(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_RADAR_ID]),
                                               npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER],
                                               int(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_COINCIDENCE_NUMBER]),
                                               npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_NOISE_PULSE_START]) )
                lAllCoincidencePerThreat[coincidenceRadarIdx].append(npArrThreatPulseLib[coincidenceRadarIdx, common.INTERVAL_LIB_PULSE_NUMBER])
            if(inCoincidence == True):
                lCoincidenceLib[-1].extend(lTempCoinc)
            else:
                lCoincidenceLib.append(lTempCoinc)

            inCoincidence = True

        # 6. update all of the pulses Tstart
        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PRI_US]

        # 7. update all of the pulses Tend
        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] + npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PW_US]

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] - npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_ENVELOPE] # shift start left for jamming bins

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_ENVELOPE] # shift end right for jamming bins


        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1

def coincidenceSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer):

    # print("Sweep through coincidences...Perform tests here...")

    dictRank= {}
    # coincBar = tqdm(total=chanItem.oCoincidences.__len__())
    __loggingTijHeader = ['Selected', 'Coinc Pulse', 'Threat ID', 'D(n) [dB]', 'Dj(n) [dB]', 'Dij(n) IJ [dB]', 'Pd IJ', 'Pulse history', 'c (CPI in coincidence)', 'j (CPI jam required)', 'm (CPI standalone)', 'JPP req', 'JPP curr', 'JPP diff', 'Rc [km]', 'Rm [km]', 'Rij [km]', 'Rb [km]', 'ZA', 'MA']
    __loggingTijData = []

    __coincBar = tqdm(total=lCoincidenceLib.__len__())
    for coincidenceIdx, coincidence in enumerate(lCoincidenceLib):
        # logging.debug("------------------------------------------------------------")
        # logging.debug( "COINCIDENCE NUMBER: %d SIZE: %d", coincidenceIdx, lCoincidenceLib.__len__())
        # logging.debug("------------------------------------------------------------")

        __loggingTijData = []

        for coincPulseIdx, coincPulse in enumerate(coincidence):

            radar_idx = coincPulse.radar_idx
            coincidencesInCPI = np.where(np.logical_and(olThreats[radar_idx].lIntervalCoincidences > (coincPulse.pulse_number - olThreats[radar_idx].oIntervalTIJStore.cpi), olThreats[radar_idx].lIntervalCoincidences <= coincPulse.pulse_number ))

            currentCPISize = olThreats[radar_idx].oIntervalTIJStore.cpi if coincPulse.pulse_number > olThreats[radar_idx].oIntervalTIJStore.cpi else coincPulse.pulse_number
            standalonePulsesInCPI = currentCPISize - coincidencesInCPI[0].__len__()

            # SNR and DETECTABILITY and INTEGRATION
            olThreats[radar_idx].oIntervalTIJStore.platformDistance_km = za.calculateplatformDistance_km(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, olThreats[radar_idx].location)

            olThreats[radar_idx].oIntervalTIJStore.SNR_dB = radarmath.radarEquationSNR(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km)

            olThreats[radar_idx].oIntervalTIJStore.SNR_NJ_dB = radarmath.radarEquationSNR_NoiseJamming(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz)

            cpiSize = 0
            if coincPulse.pulse_number < olThreats[radar_idx].oIntervalTIJStore.cpi:
                cpiSize = int(coincPulse.pulse_number)
            else:
                cpiSize = int(olThreats[radar_idx].oIntervalTIJStore.cpi)


            for Njamming in range(1, cpiSize+1):
                intermittentJammingAvg = Njamming/olThreats[radar_idx].oIntervalTIJStore.cpi
                [bJppReached, olThreats[radar_idx].oIntervalTIJStore.SNR_INJ_dB, olThreats[radar_idx].oIntervalTIJStore.Pd_min_achieved] = radarmath.radarEquationSNR_CPIJP(
                    olThreats[radar_idx].oIntervalTIJStore.cpi,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                    oPlatform.rcs,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                    olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                    oJammer.jammer_power_kW,
                    oJammer.jammer_gain_dB,
                    oJammer.jammer_bandwidth_MHz,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_DETECTION_MIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_FALSE_ALARM],
                    intermittentJammingAvg)

                if bJppReached == True:
                    if cpiSize < olThreats[radar_idx].oIntervalTIJStore.cpi:
                        if Njamming > cpiSize:
                            olThreats[radar_idx].oIntervalTIJStore.jpp_req = 1.0
                        else:
                            olThreats[radar_idx].oIntervalTIJStore.jpp_req = Njamming/cpiSize
                    else:
                        olThreats[radar_idx].oIntervalTIJStore.jpp_req = intermittentJammingAvg
                    break
                else:
                    olThreats[radar_idx].oIntervalTIJStore.jpp_req = 1.0

            olThreats[radar_idx].oIntervalTIJStore.Njamming = Njamming

            # TIJ - ZA
            ## calculate max range
            SNR_m = radarmath.calculateSNR(olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_DETECTION], olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_FALSE_ALARM], 1, 'CI')
            olThreats[radar_idx].oIntervalTIJStore.SNR_m_dB = radarmath.convertTodB(SNR_m, 10, radarmath.BASE10)
            olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km = radarmath.radarEquationRange(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                SNR_m
            )

            ## calculate min intermittent jamming range
            olThreats[radar_idx].oIntervalTIJStore.minIJRadarRange_km = radarmath.radarEquationRange_CPIJP(
                    olThreats[radar_idx].oIntervalTIJStore.cpi,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                    oPlatform.rcs,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                    SNR_m,
                    oJammer.jammer_power_kW,
                    oJammer.jammer_gain_dB,
                    oJammer.jammer_bandwidth_MHz,
                    intermittentJammingAvg
            )

            ## calculate the burnthrough range
            olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km = radarmath.radarEquationRange_CPIJP(
                    olThreats[radar_idx].oIntervalTIJStore.cpi,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                    olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                    oPlatform.rcs,
                    olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                    SNR_m,
                    oJammer.jammer_power_kW,
                    oJammer.jammer_gain_dB,
                    oJammer.jammer_bandwidth_MHz,
                    1.0
            )

            ## calculate the current range
            olThreats[radar_idx].oIntervalTIJStore.platformDistance_km = za.calculateplatformDistance_km(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, olThreats[radar_idx].location)

            ## calculate the ZA value
            olThreats[radar_idx].oIntervalTIJStore.za = za.calculateZoneAssessmentValue(olThreats[radar_idx].oIntervalTIJStore.platformDistance_km, olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km, olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km)

            # TIJ - JAMMING PULSE PERCENTAGE
            olThreats[radar_idx].oIntervalTIJStore.jpp = coincidencesInCPI[0].__len__()/cpiSize
            olThreats[radar_idx].oIntervalTIJStore.jpp_dif = olThreats[radar_idx].oIntervalTIJStore.jpp_req/olThreats[radar_idx].oIntervalTIJStore.jpp

            #TODO: TIJ - MA
            lethalRangeVal = 0
            # Lethal range flag is set to 1 if inside weapon system range
            if olThreats[radar_idx].oIntervalTIJStore.platformDistance_km <= olThreats[radar_idx].m_lethalRange_km:
                lethalRangeVal = 1

            # Ignore pulse if outside WS range AND effective intermittent jamming is achievable with standalone pulses ELSE determine mode assessment
            if lethalRangeVal == 0 and (olThreats[radar_idx].oIntervalTIJStore.Njamming <= standalonePulsesInCPI):
               olThreats[radar_idx].oIntervalTIJStore.ma = 0
            else: 
                olThreats[radar_idx].oIntervalTIJStore.ma = ma.threatValueCalculation(olThreats[radar_idx].m_mode_current_ID, olThreats[radar_idx].oIntervalTIJStore.za, lethalRangeVal, olThreats[radar_idx].oIntervalTIJStore.jpp_dif )

            # logging.debug( "************************\n")

            __loggingTijData.append(
            [
                " ",
                coincPulseIdx+1,
                olThreats[radar_idx].oIntervalTIJStore.radar_id,
                olThreats[radar_idx].oIntervalTIJStore.SNR_dB,
                olThreats[radar_idx].oIntervalTIJStore.SNR_NJ_dB,
                olThreats[radar_idx].oIntervalTIJStore.SNR_INJ_dB,
                olThreats[radar_idx].oIntervalTIJStore.Pd_min_achieved,
                coincPulse.pulse_number,
                coincidencesInCPI[0].__len__(),
                olThreats[radar_idx].oIntervalTIJStore.Njamming,
                standalonePulsesInCPI,
                olThreats[radar_idx].oIntervalTIJStore.jpp_req,
                olThreats[radar_idx].oIntervalTIJStore.jpp,
                olThreats[radar_idx].oIntervalTIJStore.jpp_dif,
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km,
                olThreats[radar_idx].oIntervalTIJStore.minIJRadarRange_km,
                olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km,
                olThreats[radar_idx].oIntervalTIJStore.za,
                olThreats[radar_idx].oIntervalTIJStore.ma
                ])

            #TODO: TIJ - TR
            dictRank[coincPulseIdx] = olThreats[radar_idx].oIntervalTIJStore.ma

        maxRankRadarId = max(dictRank, key=dictRank.get)

        # check to see of multiple of same radar in coincidence
        maxRankRadarIdx = coincidence[maxRankRadarId].radar_idx
        dictMaxRankRadar = {}
        for maxRadarInCoincidenceIdx, maxRadarInCoincidence in enumerate(coincidence):
            if(maxRankRadarIdx == maxRadarInCoincidence.radar_idx):
                dictMaxRankRadar[maxRadarInCoincidenceIdx] = maxRadarInCoincidence

        for priorityRadarKey in dictMaxRankRadar:
            priorityPulseIdx = np.max(np.where(olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences == dictMaxRankRadar[priorityRadarKey].pulse_number))
            olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences = np.delete(olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences, priorityPulseIdx)
            __loggingTijData[priorityRadarKey][0] = ">>>>>"

        dictMaxRankRadar.clear()
        dictRank.clear()

        # __loggingtable = tabulate(__loggingTijData, __loggingTijHeader, tablefmt="github")
        # logging.debug( "\n\n"+ __loggingtable +"\n\n")

        __coincBar.update(1)
    pass

def threatEvaluation(intervalIdx, olThreats, oPlatform, oJammer):
    # print("Evaluate jamming effect on threat radar...")

    for __, threat in enumerate(olThreats):
        totalDetection = 0

        # increase the pulses numbers in coincidence according to radar cpi start before its 1st interval
        if(threat.m_firstIntervalForMode == True):
            threat.lIntervalCoincidences = threat.lIntervalCoincidences + threat.m_emitter_current[common.THREAT_CPI_AT_INTERVAL]
            nplPulsesBeforeInterval = np.arange(start=1, stop=threat.m_emitter_current[common.THREAT_CPI_AT_INTERVAL], step=1)
            # add the missed radar pulses before the interval to the coincidence list -> this is all of the pulses that the jammer missed
            nplPulses = np.append(nplPulsesBeforeInterval, threat.lIntervalCoincidences)
        else:
            nplPulses = threat.lIntervalCoincidences

        # only for 1st interval of new mode thereafter we are in sync
        threat.m_firstIntervalForMode = False

        # any pulses that are not jammed
        if(nplPulses.size() > 0):
            # break into cpi chunks of available pulses
            nplCPISize = np.arange(start=threat.m_emitter_current[common.THREAT_CPI], stop=nplPulses[-1], step=threat.m_emitter_current[common.THREAT_CPI]).tolist()
            nplCpiIndices = np.zeros_like(nplCPISize)
            for cpiSizeIdx, cpiSize in enumerate(nplCPISize):
                nplCpiIndices[cpiSizeIdx] = util.find_nearestIndexFloor(nplPulses, cpiSize) + 1
            lNoJamPulsesInCPI = np.array_split(nplPulses, nplCpiIndices)

            # look out of empty arrays!
            # do radar equation with jamming for each chunk -> determine snr or Pd?
            # log the total detections
            lPdPerCPI = CheckForThreatDetectionInCPI(lNoJamPulsesInCPI, threat, oPlatform, oJammer)
            # determine if mode change is required -> or <-
            totalDetection = np.where(lPdPerCPI >= threat.m_emitter_current[common.THREAT_PROB_DETECTION])

        if(totalDetection[0].size >= threat.m_emitter_current[common.THREAT_PROB_DETECTION_CUMULATIVE]):
            if(threat.lModesForEmitter.index(threat.m_mode_current_ID) + 1 < threat.lModesForEmitter.__len__()):
                threat.m_mode_current_ID = threat.lModesForEmitter[threat.lModesForEmitter.index(threat.m_mode_current_ID) + 1]
                threat.m_emitter_current = threat.m_emitters[0][threat.lModesForEmitter.index(threat.m_mode_current_ID)]
                threat.m_mode_current_Name = common.dictModes[threat.m_mode_current_ID]
                threat.m_firstIntervalForMode = True
                
        elif (totalDetection == 0):
            if(threat.lModesForEmitter.index(threat.m_mode_current_ID) > 0):
                threat.m_mode_current_ID = threat.lModesForEmitter[threat.lModesForEmitter.index(threat.m_mode_current_ID) - 1]
                threat.m_emitter_current = threat.m_emitters[0][threat.lModesForEmitter.index(threat.m_mode_current_ID)]
                threat.m_mode_current_Name = common.dictModes[threat.m_mode_current_ID]
                threat.m_firstIntervalForMode = True

        threat.lIntervalModeChangeLog[intervalIdx + 1] = threat.m_mode_current_ID

        # any radars not in coincidence?

def CheckForThreatDetectionInCPI(lNoJamPulsesInCPI, threat, oPlatform, oJammer):

    lPdPerCPI = []
    
    for radarPulses in lNoJamPulsesInCPI:
        jammer_avgPower_kW = ((threat.oIntervalTIJStore.cpi - radarPulses.size)/threat.oIntervalTIJStore.cpi)*oJammer.jammer_power_kW

        if(jammer_avgPower_kW == 0):
            snrAchieved_dB = radarmath.radarEquationSNR(
            threat.oIntervalTIJStore.cpi,
            threat.m_emitter_current[common.THREAT_PEAKPOWER_KW],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_PW_US],
            oPlatform.rcs,
            threat.m_emitter_current[common.THREAT_FREQ_MHZ],
            threat.oIntervalTIJStore.platformDistance_km)        
        else:
            snrAchieved_dB = radarmath.radarEquationSNR_NoiseJamming(
            threat.oIntervalTIJStore.cpi,
            threat.m_emitter_current[common.THREAT_PEAKPOWER_KW],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_PW_US],
            oPlatform.rcs,
            threat.m_emitter_current[common.THREAT_FREQ_MHZ],
            threat.oIntervalTIJStore.platformDistance_km,
            jammer_avgPower_kW,
            oJammer.jammer_gain_dB,
            oJammer.jammer_bandwidth_MHz)


        lPdPerCPI.append(radarmath.calculatePd(threat.m_emitter_current[common.THREAT_PROB_FALSE_ALARM], radarmath.convertFromdB(snrAchieved_dB), 'CI'))

    return lPdPerCPI