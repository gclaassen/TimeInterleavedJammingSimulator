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
import mathRadar as radmath
import bisect

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

    __loggingRangeHeader = ['Threat ID', 'Interval Start Time [us]', 'Rc [km]', 'Rws [km]', 'Mode ID', 'Pp [kW]', 'Gtx [dBi]', 'Grx [dBi]', 'PW [us]', 'RCS [m^2]', 'Fc [MHz]', 'Ts [K]', 'CPI', 'Pfa', 'Pd', 'Pd jamming']
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

    for intervalIdx in range(0, oChannel.oInterval.intervals_total):
        logging.info("\nInterval %s of %s\n", intervalIdx+1, oChannel.oInterval.intervals_total)

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
                threatItem.m_mode_current,
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

        updateThreatsForInterval(olThreats, oChannel) # TODO: for multiple channels

        intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat)

        
        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = np.asarray(lAllCoincidencePerThreat[threatIdx])
            threatItem.lIntervalJammingPulses = [] #TODO: add pulses selected for jamming

        cpiSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer)

        # TODO: review interval
        ## TODO: update radar
        ## TODO: update jammer
        ## TODO: save interval data -> rerun purposes

        ## TODO: clear
        lCoincidenceLib = []
        lAllCoincidencePerThreat = util.initSeparateListOfObjects(olThreats.__len__())
        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = None
            threatItem.lIntervalJammingPulses = None

def updateThreatsForInterval(olThreats, oChannel):
    for __, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib[common.INTERVAL_STOP_TIME_US] = oChannel.oInterval.interval_current_Tstop_us
        pri = threatItem.m_emitter_current[common.THREAT_PRI_US] # pri
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PRI_US] = pri
        pw = threatItem.m_emitter_current[common.THREAT_PW_US] # pw
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PW_US] = pw
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PULSE_NUMBER] = 1 # always start at pulse 1 otherwise if 0 we will get division by zero

def listOfThreatsInChannel(arrThreatPulseLib, olThreats, oChannel):
    for __, threatItem in enumerate(olThreats):
        arrThreatPulseLib.append(threatItem.oThreatPulseLib)

def moveThreatPulseLibToThreatObject(npArrThreatPulseLib, olThreats):
    for threatIdx, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib = npArrThreatPulseLib[threatIdx]

def intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat):

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
            npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US]*npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_ENVELOPE]*2,
            (npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US]*npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_ENVELOPE]*2)/npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US]*100])

    __loggingtable = tabulate(__loggingCoincidenceData, __loggingCoincidenceHeader, tablefmt="github")
    logging.debug( "\n\n"+ __loggingtable +"\n\n")

    timeCounter[1] = time.perf_counter()
    logging.info( "%s seconds to complete coincidence assessor for interval %s of size %s seconds", timeCounter[1] - timeCounter[0], oChannel.oInterval.interval_current, radmath.convertTime_MicrosecondsToMilliseconds(oChannel.oInterval.interval_length_us) )

def pulseCoincidenceAssessor(npArrThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat):
    TRadarIdx = 0
    TCoincidenceIdx = 0
    inCoincidence = False

    # update times and increase pulse total
    for idx in range(npArrThreatPulseLib.__len__()):
        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW 

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] - npArrThreatPulseLib[idx, common.INTERVAL_LIB_PW_US]*(npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift start left for jamming bins

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PW_US]*(npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift end right for jamming bins
    
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

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] - npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PW_US]*(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift start left for jamming bins

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PW_US]*(npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_ENVELOPE]) # shift end right for jamming bins


        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1

def cpiSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer):

    dictRank= {}
    # coincBar = tqdm(total=chanItem.oCoincidences.__len__())
    __loggingTijHeader = ['Selected', 'Coinc Pulse', 'Threat ID', 'D(n) [dB]', 'Dj(n) [dB]', 'Dij(n) IJ [dB]', 'Pd IJ', 'Pulse history', 'c (CPI in coincidence)', 'j (CPI jammable)', 'm (CPI jamming required)', 'JPP req', 'JPP curr', 'JPP diff', 'Rc [km]', 'Rm [km]', 'Rij [km]', 'Rb [km]', 'ZA', 'MA']
    __loggingTijData = []


    for coincidenceIdx, coincidence in enumerate(lCoincidenceLib):
        logging.debug("------------------------------------------------------------")
        logging.debug( "COINCIDENCE NUMBER: %d SIZE: %d", coincidenceIdx, lCoincidenceLib.__len__())
        logging.debug("------------------------------------------------------------")

        __loggingTijData = []

        for coincPulseIdx, coincPulse in enumerate(coincidence):

            radar_idx = coincPulse.radar_idx
            CoincidencesInCPI = np.where(np.logical_and(olThreats[radar_idx].lIntervalCoincidences > (coincPulse.pulse_number - olThreats[radar_idx].oIntervalTIJStore.cpi), olThreats[radar_idx].lIntervalCoincidences <= coincPulse.pulse_number ))

            # SNR and DETECTABILITY and INTEGRATION
            olThreats[radar_idx].oIntervalTIJStore.platformDistance_km = za.calculateplatformDistance_km(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, olThreats[radar_idx].location)

            olThreats[radar_idx].oIntervalTIJStore.SNR_dB = radmath.radarEquationSNR(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km)

            olThreats[radar_idx].oIntervalTIJStore.SNR_NJ_dB = radmath.radarEquationSNR_NoiseJamming(
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
                [bJppReached, olThreats[radar_idx].oIntervalTIJStore.SNR_INJ_dB, olThreats[radar_idx].oIntervalTIJStore.Pd_min_achieved] = radmath.radarEquationSNR_CPIJP(
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


            # TIJ - JAMMING PULSE PERCENTAGE
            olThreats[radar_idx].oIntervalTIJStore.jpp = CoincidencesInCPI[0].__len__()/cpiSize


            olThreats[radar_idx].oIntervalTIJStore.jpp_dif = olThreats[radar_idx].oIntervalTIJStore.jpp_req/olThreats[radar_idx].oIntervalTIJStore.jpp

            # TIJ - ZA
            ## calculate max range
            SNR_m = radmath.calculateSNR(olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_DETECTION], olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_FALSE_ALARM], 1, 'CI')
            olThreats[radar_idx].oIntervalTIJStore.SNR_m_dB = radmath.convertTodB(SNR_m, 10, radmath.BASE10)
            olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km = radmath.radarEquationRange(
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
            olThreats[radar_idx].oIntervalTIJStore.minIJRadarRange_km = radmath.radarEquationRange_CPIJP(
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
            olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km = radmath.radarEquationRange_CPIJP(
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

            ## calcualte the ZA value
            olThreats[radar_idx].oIntervalTIJStore.za = za.calculateZoneAssessmentValue(olThreats[radar_idx].oIntervalTIJStore.platformDistance_km, olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km, olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km)

            #TODO: TIJ - MA
            lethalRangeVal = 0
            if olThreats[radar_idx].oIntervalTIJStore.platformDistance_km <= olThreats[radar_idx].m_lethalRange_km:
                lethalRangeVal = 1
            olThreats[radar_idx].oIntervalTIJStore.ma = ma.threatValueCalculation(olThreats[radar_idx].m_mode_current, olThreats[radar_idx].oIntervalTIJStore.za, lethalRangeVal, olThreats[radar_idx].oIntervalTIJStore.jpp_dif )

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
                CoincidencesInCPI[0].__len__(),
                olThreats[radar_idx].oIntervalTIJStore.Njamming,
                0, #TODO: How many signals that will be jammed in cpi
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
        dictRank.clear()
        __loggingTijData[maxRankRadarId][0] = ">>>>>"

        priorityPulseIdx = np.max(np.where(olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences == coincidence[maxRankRadarId].pulse_number))
        olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences = np.delete(olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalCoincidences, priorityPulseIdx)

        #TODO add: bisect.insort(olThreats[coincidence[maxRankRadarId].radar_idx].lIntervalPulseJammingSelectedStore, coincidence[maxRankRadarId].pulse_number)

        __loggingtable = tabulate(__loggingTijData, __loggingTijHeader, tablefmt="github")
        logging.debug( "\n\n"+ __loggingtable +"\n\n")

            #TODO: RADAR REAL

        # coincBar.update(1)
    #TODO: any radars not in coincidence?
    pass