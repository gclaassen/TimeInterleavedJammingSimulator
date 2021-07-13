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

    __loggingRangeHeader = ['Threat ID', 'Interval Start Time [us]', 'Rm [km]', 'Rb km', 'Rc [km]', 'Rws [km]', 'Mode', 'Pp [kW]', 'Gtx [dBi]', 'Grx [dBi]', 'PW [us]', 'RCS [m^2]', 'Fc [MHz]', 'Ts [K]', 'CPI', 'Pfa', 'Pd', 'Pd jamming']
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
        threat.lIntervalCoincidencePercentageLog = np.zeros(oChannel.oInterval.intervals_total)
        threat.lIntervalZoneAssessmentLog = np.zeros(oChannel.oInterval.intervals_total)
        threat.lIntervalLethalRangeLog = np.zeros(oChannel.oInterval.intervals_total)
        threat.lIntervalJammingLog = np.zeros(oChannel.oInterval.intervals_total)
        threat.lDetectionsInIntervalLog = np.zeros(oChannel.oInterval.intervals_total)
        threat.lIntervalModeChangeLog = np.zeros(oChannel.oInterval.intervals_total+1)
        threat.lIntervalModeChangeLog[0] = threat.m_mode_current_ID

    logInitialThreatParametersForAllModes(olThreats, oPlatform, oJammer)

    for intervalIdx in range(0, oChannel.oInterval.intervals_total):
        logging.info("\nInterval %s of %s\n", intervalIdx+1, oChannel.oInterval.intervals_total)

        oChannel.oInterval.interval_current = intervalIdx
        oChannel.oInterval.interval_current_Tstart_us = oChannel.interval_time_us * intervalIdx
        if((intervalIdx + 1) == oChannel.oInterval.intervals_total):
            oChannel.oInterval.interval_current_Tstop_us = oPlatform.timeStop_us
        else:
            oChannel.oInterval.interval_current_Tstop_us = oChannel.oInterval.interval_current_Tstart_us + oJammer.oChannel[0].interval_time_us

        updateThreatsForInterval(olThreats, oChannel, oJammer.jammer_bin_size_pri, oJammer.jammer_bin_size_pw) # TODO: for multiple channels

        # __logging__
        # Get the starting ranges at each new interval
        __loggingRangeData = []

        for threatIdx, threatItem in enumerate(olThreats):
            ## calculate current range
            RadarDistance_km = za.calculateplatformDistance_km(oChannel.oInterval.interval_current_Tstart_us, oPlatform.flightPath, threatItem.location)
            ## calculate max range
            threatItem.oIntervalTIJStore.maxRadarRange_km = radarmath.radarEquationRange(
                threatItem.oIntervalTIJStore.cpi,
                threatItem.m_emitter_current[common.THREAT_PEAKPOWER_KW],
                threatItem.m_emitter_current[common.THREAT_GAIN],
                threatItem.m_emitter_current[common.THREAT_GAIN],
                threatItem.m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                threatItem.m_emitter_current[common.THREAT_FREQ_MHZ],
                threatItem.oIntervalTIJStore.SNR_n,
                threatItem.m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
                threatItem.m_mode_current_ID,
                threatItem.m_emitter_current[common.THREAT_PRI_US]
            )

            ## calculate the burnthrough range
            threatItem.oIntervalTIJStore.burnthroughRange_km = radarmath.radarEquationRange_CPIJP(
                    threatItem.oIntervalTIJStore.cpi,
                    threatItem.m_emitter_current[common.THREAT_PEAKPOWER_KW],
                    threatItem.m_emitter_current[common.THREAT_GAIN],
                    threatItem.m_emitter_current[common.THREAT_GAIN],
                    threatItem.m_emitter_current[common.THREAT_PW_US],
                    oPlatform.rcs,
                    threatItem.m_emitter_current[common.THREAT_FREQ_MHZ],
                    threatItem.oIntervalTIJStore.SNR_n,
                    oJammer.jammer_power_kW,
                    oJammer.jammer_gain_dB,
                    oJammer.jammer_bandwidth_MHz,
                    threatItem.m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
                    1.0,
                    threatItem.m_mode_current_ID,
                    threatItem.m_emitter_current[common.THREAT_PRI_US]
            )

            __loggingRangeData.append([
                threatIdx+1,
                oChannel.oInterval.interval_current_Tstart_us,
                threatItem.oIntervalTIJStore.maxRadarRange_km,
                threatItem.oIntervalTIJStore.burnthroughRange_km,
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
                threatItem.m_emitter_current[common.THREAT_PROB_DETECTION_MIN]
                ])

        __loggingtable = tabulate(__loggingRangeData, __loggingRangeHeader, tablefmt="github")
        logging.debug( "\n\n"+ __loggingtable +"\n\n")

        intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat, intervalIdx)

        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = np.asarray(lAllCoincidencePerThreat[threatIdx])
            threatItem.lIntervalJammingPulses = [] #TODO: add pulses selected for jamming

        coincidenceSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer, intervalIdx)

        # review interval
        ## update radar
        threatEvaluation(intervalIdx, olThreats, oPlatform, oJammer)

        # logging data to save
        intervalThreatLoggingData(olThreats, intervalIdx)

        ## clear
        lCoincidenceLib = []
        lAllCoincidencePerThreat = util.initSeparateListOfObjects(olThreats.__len__())
        for threatIdx, threatItem in enumerate(olThreats):
            threatItem.lIntervalCoincidences = None
            threatItem.lIntervalJammingPulses = None

    logging.info("Post scenario stats:\n")
    for __, threat in enumerate(olThreats):
        logging.info("Threat Radar {0}: Modes Available: {1}".format(threat.m_radar_id, threat.lModesForEmitter))
    for __, threat in enumerate(olThreats):
        logging.info("Threat Radar {0}: Mode Changes: {1}".format(threat.m_radar_id, threat.lIntervalModeChangeLog))

def updateThreatsForInterval(olThreats, oChannel, jammerEnvelopeSizeToPRI, jammerEnvelopeSizeToPW):
    for __, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib[common.INTERVAL_STOP_TIME_US] = oChannel.oInterval.interval_current_Tstop_us
        pri = threatItem.m_emitter_current[common.THREAT_PRI_US] # pri
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PRI_US] = pri
        pw = threatItem.m_emitter_current[common.THREAT_PW_US] # pw
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PW_US] = pw
        if common.ARG_JAMMINGBINPRI:
            if jammerEnvelopeSizeToPRI == 0:
                jammingBound_us = 0
            else:
                jammingEnvelope = pri * jammerEnvelopeSizeToPRI
                jammingBound_us = (jammingEnvelope)/2 if jammingEnvelope > pw else pw*0.75
                threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - pw/2
        else:
            if common.ARG_CUTPULSEATEND:
                jammingEnvelopeStart = pw * jammerEnvelopeSizeToPW
                jammingBound_us = (jammingEnvelopeStart)/2
                jammingEnvelopeStop = pw * 0.05 # cover pulse fall time is 5% of pulse width
                threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = jammingBound_us - pw/2
                threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingEnvelopeStop
            else:
                if jammerEnvelopeSizeToPW == 0:
                    jammingBound_us = 0
                    threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - pw/2
                else:
                    jammingEnvelope = pw * jammerEnvelopeSizeToPW
                    jammingBound_us = (jammingEnvelope)/2
                    threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_START_ENVELOPE] = threatItem.oThreatPulseLib[common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] = jammingBound_us - pw/2

        threatItem.oThreatPulseLib[common.INTERVAL_LIB_COINCIDENCE_NUMBER] = 0
        threatItem.oThreatPulseLib[common.INTERVAL_LIB_PULSE_NUMBER] = 1 # always start at pulse 1 otherwise if 0 we will get division by zero

        threatItem.oIntervalTIJStore.cpi = threatItem.m_emitter_current[common.THREAT_CPI]

        threatItem.oIntervalTIJStore.SNR_1 = radarmath.calculateSNR(threatItem.m_emitter_current[common.THREAT_PROB_DETECTION], threatItem.m_emitter_current[common.THREAT_PROB_FALSE_ALARM], 1, 'CI')

        threatItem.oIntervalTIJStore.SNR_n = radarmath.calculateSNR(threatItem.m_emitter_current[common.THREAT_PROB_DETECTION], threatItem.m_emitter_current[common.THREAT_PROB_FALSE_ALARM], threatItem.oIntervalTIJStore.cpi, 'CI')

        threatItem.oIntervalTIJStore.SNR_1_dB = radarmath.convertTodB(threatItem.oIntervalTIJStore.SNR_1, 10, radarmath.BASE10)
        threatItem.oIntervalTIJStore.SNR_n_dB = radarmath.convertTodB(threatItem.oIntervalTIJStore.SNR_n, 10, radarmath.BASE10)

def listOfThreatsInChannel(arrThreatPulseLib, olThreats, oChannel):
    for __, threatItem in enumerate(olThreats):
        arrThreatPulseLib.append(threatItem.oThreatPulseLib)

def moveThreatPulseLibToThreatObject(npArrThreatPulseLib, olThreats):
    for threatIdx, threatItem in enumerate(olThreats):
        threatItem.oThreatPulseLib = npArrThreatPulseLib[threatIdx]

def intervalCoincidenceCalculator(olThreats, oChannel, lCoincidenceLib, lAllCoincidencePerThreat, intervalIdx):

    # print("Determining coincidences...Please wait")
    arrThreatPulseLib = []

    timeCounter = [0]*2 # start and stop
    __loggingCoincidenceHeader = ['Threat ID', 'Pulses', 'PRI [us]', 'PW [us]', 'Duty Cycle [%]', 'Jamming Coincidences', 'c/p [%]', 'Jamming PW [us]', 'Jamming Duty Cycle [%]']
    __loggingCoincidenceData = []

    timeCounter[0] = time.perf_counter()

    listOfThreatsInChannel(arrThreatPulseLib, olThreats, oChannel)
    npArrThreatPulseLib = np.array(arrThreatPulseLib)

    pulseCoincidenceAssessor(npArrThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat)

    logging.info("Stats:\ttotal coincidences: %d\n", lCoincidenceLib.__len__())

    npArrThreatPulseLib[:, common.INTERVAL_INTERVAL_COINCIDENCE_PERC] = npArrThreatPulseLib[:, common.INTERVAL_LIB_COINCIDENCE_NUMBER] / npArrThreatPulseLib[:, common.INTERVAL_LIB_PULSE_NUMBER]

    moveThreatPulseLibToThreatObject(npArrThreatPulseLib, olThreats)

    for __, threat in enumerate(olThreats):
        threat.lIntervalCoincidencePercentageLog[intervalIdx] = threat.oThreatPulseLib[common.INTERVAL_INTERVAL_COINCIDENCE_PERC]

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
            npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_START_ENVELOPE] + npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE],
            (npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_START_ENVELOPE] + npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PW_US] + npArrThreatPulseLib[logIdx, common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE])/npArrThreatPulseLib[logIdx, common.INTERVAL_LIB_PRI_US]*100])

    __loggingtable = tabulate(__loggingCoincidenceData, __loggingCoincidenceHeader, tablefmt="github")
    logging.debug( "\n\n"+ __loggingtable +"\n\n")

    timeCounter[1] = time.perf_counter()
    logging.info( "%s seconds to complete coincidence assessor for interval %s of size %s seconds", timeCounter[1] - timeCounter[0], oChannel.oInterval.interval_current, radarmath.convertTime_MicrosecondsToSeconds(oChannel.oInterval.interval_length_us) )

def pulseCoincidenceAssessor(npArrThreatPulseLib, lCoincidenceLib, lAllCoincidencePerThreat):
    TRadarIdx = 0
    TCoincidenceIdx = 0
    inCoincidence = False

    # update times and increase pulse total
    for idx in range(npArrThreatPulseLib.__len__()):
        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PRI_US] # Tstart = Tend + PRI

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] + npArrThreatPulseLib[idx, common.INTERVAL_LIB_PW_US] # Tend = Tstart + PW

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_START] - (npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_START_ENVELOPE]) # shift start left for jamming bins

        npArrThreatPulseLib[idx, common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[idx, common.INTERVAL_LIB_PULSE_STOP] + (npArrThreatPulseLib[idx, common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE]) # shift end right for jamming bins

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

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_START] = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_START] - npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_START_ENVELOPE] # shift start left for jamming bins

        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_NOISE_PULSE_STOP]  = npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_STOP] + npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_JAMMING_BIN_STOP_ENVELOPE] # shift end right for jamming bins


        npArrThreatPulseLib[TCoincidenceIdx[0], common.INTERVAL_LIB_PULSE_NUMBER] += 1

def coincidenceSweeper(lCoincidenceLib, olThreats, oPlatform, oJammer, intervalIdx):

    # print("Sweep through coincidences...Perform tests here...")

    dictRank = {}
    # modeRank = []
    __loggingTijHeader = ['Selected', 'Coinc Pulse', 'Threat ID', 'D(n) [dB]', 'Dj(n) [dB]', 'Dij(n) IJ [dB]', 'Pd IJ', 'Pulse history', 'c (CPI in coincidence)', 'j (CPI jam required)', 'm (CPI standalone)', 'JCP', 'Rc [km]', 'Rm [km]', 'Rij [km]', 'Rb [km]', 'ZA', 'MA']
    __loggingTijData = []

    __coincBarDescr = "Interval " + str(intervalIdx)
    __coincBar = tqdm(total=lCoincidenceLib.__len__(),desc=__coincBarDescr)
    for coincidenceIdx, coincidence in enumerate(lCoincidenceLib):
        # logging.debug("------------------------------------------------------------")
        # logging.debug( "COINCIDENCE NUMBER: %d SIZE: %d", coincidenceIdx, lCoincidenceLib.__len__())
        # logging.debug("------------------------------------------------------------")

        __loggingTijData = []

        for coincPulseIdx, coincPulse in enumerate(coincidence):

            radar_idx = coincPulse.radar_idx
            coincidencesInCPI = np.where(np.logical_and(olThreats[radar_idx].lIntervalCoincidences > (coincPulse.pulse_number - olThreats[radar_idx].oIntervalTIJStore.cpi), olThreats[radar_idx].lIntervalCoincidences <= coincPulse.pulse_number ))

            OuterIntervalPulses = 0 if coincPulse.pulse_number > olThreats[radar_idx].oIntervalTIJStore.cpi else (olThreats[radar_idx].oIntervalTIJStore.cpi - coincPulse.pulse_number)
            coincidencesInCPI = coincidencesInCPI[0].__len__() + OuterIntervalPulses
            standalonePulsesInCPI = olThreats[radar_idx].oIntervalTIJStore.cpi - coincidencesInCPI

            # SNR and DETECTABILITY and INTEGRATION
            # TIJ - ZA
            ## calculate the current range
            olThreats[radar_idx].oIntervalTIJStore.platformDistance_km = za.calculateplatformDistance_km(coincPulse.timeOfCoincidence_us, oPlatform.flightPath, olThreats[radar_idx].location)

            olThreats[radar_idx].oIntervalTIJStore.SNR_dB = radarmath.radarEquationSNR(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                olThreats[radar_idx].m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
                olThreats[radar_idx].m_mode_current_ID,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PRI_US])

            olThreats[radar_idx].oIntervalTIJStore.SNR_NJ_dB = radarmath.radarEquationSNR_CPIJP(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                olThreats[radar_idx].m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
                oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz,
                olThreats[radar_idx].m_mode_current_ID,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PRI_US])

            cpiSize = 0
            if coincPulse.pulse_number < olThreats[radar_idx].oIntervalTIJStore.cpi:
                cpiSize = int(coincPulse.pulse_number)
            else:
                cpiSize = int(olThreats[radar_idx].oIntervalTIJStore.cpi)

            ## calculate the ZA value
            olThreats[radar_idx].oIntervalTIJStore.za = za.calculateZoneAssessmentValue(olThreats[radar_idx].oIntervalTIJStore.platformDistance_km, olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km, olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km)

            # TIJ - JAMMING PULSE PERCENTAGE
            Njamming = 0
            for Njamming in range(1, olThreats[radar_idx].oIntervalTIJStore.cpi+1):
                olThreats[radar_idx].oIntervalTIJStore.jammingPercentage = Njamming/olThreats[radar_idx].oIntervalTIJStore.cpi
                olThreats[radar_idx].oIntervalTIJStore.SNR_INJ_dB = radarmath.radarEquationSNR_CPIJP(
                olThreats[radar_idx].oIntervalTIJStore.cpi,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PEAKPOWER_KW],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_GAIN],
                olThreats[radar_idx].m_emitter_current[common.THREAT_PW_US],
                oPlatform.rcs,
                olThreats[radar_idx].m_emitter_current[common.THREAT_FREQ_MHZ],
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                olThreats[radar_idx].m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
                olThreats[radar_idx].oIntervalTIJStore.jammingPercentage * oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz,
                olThreats[radar_idx].m_mode_current_ID,
                olThreats[radar_idx].m_emitter_current[common.THREAT_PRI_US])

                olThreats[radar_idx].oIntervalTIJStore.Pd_min_achieved = radarmath.calculatePd(olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_FALSE_ALARM], radarmath.convertFromdB(olThreats[radar_idx].oIntervalTIJStore.SNR_INJ_dB), 'CI')

                if(olThreats[radar_idx].oIntervalTIJStore.Pd_min_achieved <= olThreats[radar_idx].m_emitter_current[common.THREAT_PROB_DETECTION_MIN]):
                    break

            olThreats[radar_idx].oIntervalTIJStore.Njamming = Njamming

            # Lethal range flag is set to 1 if inside weapon system range
            olThreats[radar_idx].oIntervalTIJStore.lethalRangeVal = 1 if olThreats[radar_idx].oIntervalTIJStore.platformDistance_km <= olThreats[radar_idx].m_lethalRange_km else 0

            # Ignore pulse if outside WS range AND effective intermittent jamming is achievable with standalone pulses ELSE determine mode assessment
            if olThreats[radar_idx].oIntervalTIJStore.lethalRangeVal == 0 and (olThreats[radar_idx].oIntervalTIJStore.Njamming <= standalonePulsesInCPI):
               olThreats[radar_idx].oIntervalTIJStore.ma = 0
            else:
                # jamming coincidence percentage
                if olThreats[radar_idx].oIntervalTIJStore.Njamming > standalonePulsesInCPI:
                    olThreats[radar_idx].oIntervalTIJStore.jcp = (olThreats[radar_idx].oIntervalTIJStore.Njamming - standalonePulsesInCPI) /coincidencesInCPI
                elif olThreats[radar_idx].oIntervalTIJStore.Njamming <= standalonePulsesInCPI:
                    olThreats[radar_idx].oIntervalTIJStore.jcp = 0

                # mode assessment calculation
                olThreats[radar_idx].oIntervalTIJStore.ma = ma.threatValueCalculation(olThreats[radar_idx].m_mode_current_ID, olThreats[radar_idx].oIntervalTIJStore.za, olThreats[radar_idx].oIntervalTIJStore.lethalRangeVal, olThreats[radar_idx].oIntervalTIJStore.jcp )

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
                coincidencesInCPI,
                olThreats[radar_idx].oIntervalTIJStore.Njamming,
                standalonePulsesInCPI,
                olThreats[radar_idx].oIntervalTIJStore.jcp,
                olThreats[radar_idx].oIntervalTIJStore.platformDistance_km,
                olThreats[radar_idx].oIntervalTIJStore.maxRadarRange_km,
                olThreats[radar_idx].oIntervalTIJStore.minIJRadarRange_km,
                olThreats[radar_idx].oIntervalTIJStore.burnthroughRange_km,
                olThreats[radar_idx].oIntervalTIJStore.za,
                olThreats[radar_idx].oIntervalTIJStore.ma
                ])

            dictRank[coincPulseIdx] = olThreats[radar_idx].oIntervalTIJStore.ma
            # modeRank.append([olThreats[radar_idx].oIntervalTIJStore.radar_id, olThreats[radar_idx].m_mode_current_ID, olThreats[radar_idx].oIntervalTIJStore.za])

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

        # if(TestType == common.TEST_HIGHESTMODE):

        #     npModeRank = np.array(modeRank)
        #     npModeRank = npModeRank[npModeRank[:, 1].argsort()][::-1]
        #     npModeRank = npModeRank[npModeRank[:,2].argsort(kind='mergesort')][::-1]

        #     threatId = npModeRank[0,0]

        #     for coincidenceThreatIdx, coincidenceThreat in enumerate(coincidence):
        #         if(int(threatId) == coincidenceThreat.radar_id):
        #             threatIdx = coincidenceThreat.radar_idx
        #             priorityPulseIdx = np.max(np.where(olThreats[threatIdx].lIntervalCoincidences == coincidenceThreat.pulse_number))
        #             olThreats[threatIdx].lIntervalCoincidences = np.delete(olThreats[threatIdx].lIntervalCoincidences, priorityPulseIdx)
        #             __loggingTijData[coincidenceThreatIdx][0] = ">>>>>"

        # modeRank = []


        # __loggingtable = tabulate(__loggingTijData, __loggingTijHeader, tablefmt="github")
        # logging.debug( "\n\n"+ __loggingtable +"\n\n")

        __coincBar.update(1)
    pass

def threatEvaluation(intervalIdx, olThreats, oPlatform, oJammer):
    # print("Evaluate jamming effect on threat radar...")

    for __, threat in enumerate(olThreats):
        totalDetection = 0

        #TODO: what if cpi not reached

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
        if(nplPulses.size > 0):
            # break into cpi chunks of available pulses
            nplCPISize = np.arange(start=threat.m_emitter_current[common.THREAT_CPI], stop=nplPulses[-1], step=threat.m_emitter_current[common.THREAT_CPI]).tolist()
            nplCpiIndices = np.zeros_like(nplCPISize)
            for cpiSizeIdx, cpiSize in enumerate(nplCPISize):
                nearestIndex = util.find_nearestIndexFloor(nplPulses, cpiSize)
                if(nearestIndex != None):
                    nplCpiIndices[cpiSizeIdx] = util.find_nearestIndexFloor(nplPulses, cpiSize) + 1
                else:
                    nplCpiIndices[cpiSizeIdx] = 0
            lNoJamPulsesInCPI = np.array_split(nplPulses, nplCpiIndices)

            # look out of empty arrays!
            # do radar equation with jamming for each chunk -> determine snr or Pd?
            # log the total detections
            lPdPerCPI = CheckForThreatDetectionInCPI(lNoJamPulsesInCPI, threat, oPlatform, oJammer)
            # determine if mode change is required -> or <-
            lFindDetections = np.where(lPdPerCPI >= threat.m_emitter_current[common.THREAT_PROB_DETECTION])
            totalDetection = lFindDetections[0].size

        if(totalDetection >= threat.m_emitter_current[common.THREAT_PROB_DETECTION_CUMULATIVE]):
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

        threat.lDetectionsInIntervalLog[intervalIdx] = totalDetection

        threat.lIntervalModeChangeLog[intervalIdx + 1] = threat.m_mode_current_ID


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
            threat.oIntervalTIJStore.platformDistance_km,
            threat.m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
            threat.m_mode_current_ID,
            threat.m_emitter_current[common.THREAT_PRI_US])
        else:
            snrAchieved_dB = radarmath.radarEquationSNR_CPIJP(
            threat.oIntervalTIJStore.cpi,
            threat.m_emitter_current[common.THREAT_PEAKPOWER_KW],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_GAIN],
            threat.m_emitter_current[common.THREAT_PW_US],
            oPlatform.rcs,
            threat.m_emitter_current[common.THREAT_FREQ_MHZ],
            threat.oIntervalTIJStore.platformDistance_km,
            threat.m_emitter_current[common.THREAT_EMITTER_NOISEFIGURE_DB],
            jammer_avgPower_kW,
            oJammer.jammer_gain_dB,
            oJammer.jammer_bandwidth_MHz,
            threat.m_mode_current_ID,
            threat.m_emitter_current[common.THREAT_PRI_US])


        lPdPerCPI.append(radarmath.calculatePd(threat.m_emitter_current[common.THREAT_PROB_FALSE_ALARM], radarmath.convertFromdB(snrAchieved_dB), 'CI'))

    return lPdPerCPI

def intervalThreatLoggingData(olThreats, index):
    for __, threat in enumerate(olThreats):

        # the za value
        threat.lIntervalZoneAssessmentLog[index] = threat.oIntervalTIJStore.za

        # the lethal range flag
        threat.lIntervalLethalRangeLog[index] = threat.oIntervalTIJStore.lethalRangeVal

        # intermittent jamming requirement
        threat.lIntervalJammingLog[index] = threat.oIntervalTIJStore.jammingPercentage

def logInitialThreatParametersForAllModes(olThreats, oPlatform, oJammer):

    __loggingThreatHeader = ['Threat ID', 'Mode ID', 'Rm [km]', 'Rb km', 'Rc [km]', 'Pd min Rm', 'Pd Rc', 'CPI', 'IJ Rm', 'IJ Rc', 'PRF']
    __loggingThreatData = []

    for __, threat in enumerate(olThreats):
        for __, mode in enumerate(threat.m_emitters[0]):
            SNR_n = radarmath.calculateSNR(mode[common.THREAT_PROB_DETECTION], mode[common.THREAT_PROB_FALSE_ALARM], mode[common.THREAT_CPI], 'CI')

            platformDistance_km = za.calculateplatformDistance_km(0, oPlatform.flightPath, threat.location)

            ## calculate max range
            maxRadarRange_km = radarmath.radarEquationRange(
                mode[common.THREAT_CPI],
                mode[common.THREAT_PEAKPOWER_KW],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_PW_US],
                oPlatform.rcs,
                mode[common.THREAT_FREQ_MHZ],
                SNR_n,
                mode[common.THREAT_EMITTER_NOISEFIGURE_DB],
                mode[common.THREAT_MODE_ID],
                mode[common.THREAT_PRI_US]
            )

            ## calculate the burnthrough range
            burnthroughRange_km = radarmath.radarEquationRange_CPIJP(
                    mode[common.THREAT_CPI],
                    mode[common.THREAT_PEAKPOWER_KW],
                    mode[common.THREAT_GAIN],
                    mode[common.THREAT_GAIN],
                    mode[common.THREAT_PW_US],
                    oPlatform.rcs,
                    mode[common.THREAT_FREQ_MHZ],
                    SNR_n,
                    oJammer.jammer_power_kW,
                    oJammer.jammer_gain_dB,
                    oJammer.jammer_bandwidth_MHz,
                    mode[common.THREAT_EMITTER_NOISEFIGURE_DB],
                    1.0,
                    mode[common.THREAT_MODE_ID],
                    mode[common.THREAT_PRI_US]
            )

            Njamming = 0
            for Njamming in range(1, mode[common.THREAT_CPI],+1):
                jammingPercentage = Njamming/mode[common.THREAT_CPI]
                SNR_INJ_dB = radarmath.radarEquationSNR_CPIJP(
                mode[common.THREAT_CPI],
                mode[common.THREAT_PEAKPOWER_KW],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_PW_US],
                oPlatform.rcs,
                mode[common.THREAT_FREQ_MHZ],
                platformDistance_km,
                mode[common.THREAT_EMITTER_NOISEFIGURE_DB],
                jammingPercentage * oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz,
                mode[common.THREAT_MODE_ID],
                mode[common.THREAT_PRI_US])

                Pd_min_achieved_plf_range = radarmath.calculatePd(mode[common.THREAT_PROB_FALSE_ALARM], radarmath.convertFromdB(SNR_INJ_dB), 'CI')

                if(Pd_min_achieved_plf_range <= mode[common.THREAT_PROB_DETECTION_MIN]):
                    break

            Njamming_maxRange = 0
            for Njamming_maxRange in range(1, mode[common.THREAT_CPI],+1):
                jammingPercentage = Njamming_maxRange/mode[common.THREAT_CPI]
                SNR_INJ_dB = radarmath.radarEquationSNR_CPIJP(
                mode[common.THREAT_CPI],
                mode[common.THREAT_PEAKPOWER_KW],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_GAIN],
                mode[common.THREAT_PW_US],
                oPlatform.rcs,
                mode[common.THREAT_FREQ_MHZ],
                maxRadarRange_km,
                mode[common.THREAT_EMITTER_NOISEFIGURE_DB],
                jammingPercentage * oJammer.jammer_power_kW,
                oJammer.jammer_gain_dB,
                oJammer.jammer_bandwidth_MHz,
                mode[common.THREAT_MODE_ID],
                mode[common.THREAT_PRI_US])

                Pd_min_achieved_max_range = radarmath.calculatePd(mode[common.THREAT_PROB_FALSE_ALARM], radarmath.convertFromdB(SNR_INJ_dB), 'CI')

                if(Pd_min_achieved_max_range <= mode[common.THREAT_PROB_DETECTION_MIN]):
                    break

            __loggingThreatData.append([
                threat.m_radar_id,
                mode[common.THREAT_MODE_ID],
                maxRadarRange_km,
                burnthroughRange_km,
                platformDistance_km,
                Pd_min_achieved_max_range,
                Pd_min_achieved_plf_range,
                mode[common.THREAT_CPI],
                Njamming_maxRange,
                Njamming,
                mode[common.THREAT_PRI_US]*0.05])

    __loggingtable = tabulate(__loggingThreatData, __loggingThreatHeader, tablefmt="github")
    logging.debug( "\n\n"+ __loggingtable +"\n\n")