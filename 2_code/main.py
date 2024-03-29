import os
import getopt
import sys 
import traceback
import threats
import pltf as platform
import jammer
import common
import jsonParser
import visualize
import numpy as np
import intervalProcess as interval
import logging
import tij
# save numpy array as npy file
from numpy import asarray
from numpy import save
import shutil

# logging.basicConfig(level = logging.DEBUG)
# comment to print to console, uncomment to save to log file
logging.basicConfig(filename='tij.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S', level = logging.DEBUG)
np.set_printoptions(precision=5, suppress=True)

def argumentExtraction(argv):
    setViz = False
    interFile = None
    Wm = 0
    Wz = 0
    Wl = 0
    Wj = 0
    choosePRIJamming = False
    cutPulseAtEnd = False
    experimentalWindowSize = False
    ignoreBurnthrough = False
    selectOnlyHighestPulsesInCoinc = False
    randomPulseStart = False

    try:
        [opts, argv] = getopt.getopt(
            argv, "hvpcetrb:i:m:z:l:j:",
            ["help", "visualize", "PRIBin", "cutPulseAtEnd", "experimentalWindowSize", "selectOnlyHighestPulsesInCoinc", "randomPulseStart",  "ignoreBurnthrough", "intermediaryDirectory=", "modeWeight=", "zoneWeight=", "lethalrangeWeight=", "intermittentJammingWeight="])
    except getopt.GetoptError:
        helpPrints()
    for opt, arg in opts:
        if opt == '-h':
            helpPrints()
            exit()
        elif opt in ("-v", "--visualize"):
            setViz = True
            logging.info('Visualization set to True')
        elif opt in ("-p", "--PRIBin"):
            logging.info('Jamming window is 10% of PRI')
            choosePRIJamming = True
        elif opt in ("-b", "--ignoreBurnthrough"):
            ignoreBurnthrough = True
            logging.info('Ignore radars in burnthrough')
        elif opt in ("-r", "--randomPulseStart"):
            randomPulseStart = True
            logging.info('Start random pulse start')
        elif opt in ("-t", "--selectOnlyHighestPulsesInCoinc"):
            selectOnlyHighestPulsesInCoinc = True
            logging.info('Iterate in coincidence and select highest priority non overlapping pulses')
        elif opt in ("-c", "--cutPulseAtEnd"):
            cutPulseAtEnd = True
            logging.info('Jamming window: PW cut at end selected')
        elif opt in ("-e", "--experimentalWindowSize"):
            experimentalWindowSize = True
            logging.info('Jamming window: Experimental window size')
        elif opt in ("-i", "--intermediaryDirectory"):
            interFile = arg + '/'
            logging.info('Intermediary File: {0}'.format(interFile))
        elif opt in ("-m", "--modeWeight"):
            Wm = float(arg)
            logging.info('Mode weight: {0}'.format(arg))
        elif opt in ("-z", "--zoneWeight"):
            Wz = float(arg)
            logging.info('Zone assessment weight: {0}'.format(arg))
        elif opt in ("-l", "--lethalrangeWeight"):
            Wl = float(arg)
            logging.info('Lethal range weight: {0}'.format(arg))
        elif opt in ("-j", "--intermittentJammingWeight"):
            Wj = float(arg)
            logging.info('Intermittent jamming weight: {0}'.format(arg))

    return [interFile, Wm, Wz, Wl, Wj, choosePRIJamming, cutPulseAtEnd, experimentalWindowSize, ignoreBurnthrough, selectOnlyHighestPulsesInCoinc, randomPulseStart, setViz]

def helpPrints():
    logging.info('\npyTIJ.py <arguments> \n')
    logging.info('~~~ARGUMENT LIST~~~\n')
    logging.info('-v:\tvisualize\n')
    logging.info('-p:\tselect jamming window to PRI\n')
    logging.info('-c:\tCut pulse at end\n')
    logging.info('-e:\tJamming window experimental\n')
    logging.info('-i:\tintermediary directory\n')
    logging.info('-m:\tmode weight\n')
    logging.info('-z:\zone assessment weight\n')
    logging.info('-l:\lethal range weight\n')
    logging.info('-j:\intermittent jamming weight\n')
    logging.info('-b:\ignore the radar pulses in burnthrough\n')
    logging.info('-r:\the starting pulses for each radar at each interval starts at random time between 0 and the PRI')
    logging.info('-t:\Iterate in coincidence and select highest priority non overlapping pulses otherwise all the pulses of the same radar in coincidence will be selected first before checking the overlap pulses.\n')

def main(argv):
    doViz = False
    interFile = None

    [interFile,
    common.MA_MODE_WEIGHT,
    common.MA_ZA_WEIGHT,
    common.MA_LETHALRANGE_WEIGHT,
    common.MA_INTERMITTENTJAMMING_WEIGHT,
    common.ARG_JAMMINGBINPRI,
    common.ARG_CUTPULSEATEND,
    common.ARG_JAMMINGWINDOWEXPERIMENTAL,
    common.IGNOREBURNTHROUGH,
    common.SELECTHIGHESTITERATE,
    common.ARG_RANDOMSTART,
    doViz] = argumentExtraction(argv)

    # Initialize
    [oPlatform, oJammer, olThreats] = initEnvironment(interFile)

    initThreatsForTij(olThreats, oJammer)

    #! visualize the world
    # if doViz:
        # visualize.topview(oPlatform, olThreats)

    #! Single jamming channel
    interval.intervalProcessorSingleChannel(oPlatform, oJammer, olThreats, oJammer.oChannel[0])
    # save data
    saveThreatData(olThreats, interFile, oJammer.oChannel[0].oInterval.intervals_total)

    #! TODO: Multiple jamming channels
    #     logging.info("Number of processors: %s", mp.Pool(mp.cpu_count()))
    # retList = mp.Pool(oChannel.__len__()).map(interval.intervalProcessor, [oPlatform, oJammer, olThreats, oJammer.oChannel])

    pass

def initThreatsForTij(threat, jammer):
    for threatItem in threat:
        threatItem.oThreatPulseLib = np.array(threats.initListThreatPulseLib(threatItem, jammer), dtype=object)
        new_cTij = tij.cTIJ(threatItem.m_radar_id, threatItem.m_emitter_current[common.THREAT_CPI], threatItem.m_emitter_current[common.THREAT_PROB_FALSE_ALARM], threatItem.m_emitter_current[common.THREAT_PROB_DETECTION], threatItem.m_emitter_current[common.THREAT_PROB_DETECTION_MIN])
        threatItem.oIntervalTIJStore = new_cTij


def initEnvironment(interFile):
    # init platform class instance
    platformPath = os.path.join(common.PLATFORMDIR, interFile)
    oPlatform = platform.cPlatform(jsonParser.parseJsonFile( platformPath + common.PLATFORMFILE))

    # init threats (mulitple instances of threat class)
    threatPath = os.path.join(common.THREATDIR, interFile)
    olThreats = threats.convertThreatJsonToClass(jsonParser.parseJsonFile(threatPath + common.THREATFILE))

    # init jammer
    jammerPath = os.path.join(common.JAMMERDIR, interFile)
    oJammer = jammer.cJammer(jsonParser.parseJsonFile(jammerPath + common.JAMMERFILE))

    # profile creator
    for itChannel in oJammer.oChannel:
        itChannel.oInterval = interval.cInterval(itChannel.interval_time_us, oPlatform.timeStop_us )

    return [oPlatform, oJammer, olThreats]

def saveThreatData(olThreats, interFile, intervalSize):
    vlModeLog = np.zeros((0,intervalSize+1))
    vlRangeLog = np.zeros((0,intervalSize))
    vlLethalRangeLog = np.zeros((0,intervalSize))
    vlCoincPercLog = np.zeros((0,intervalSize))
    vlJammingLog = np.zeros((0,intervalSize))
    vlDetectionLog = np.zeros((0,intervalSize))
    vlCPILog = np.zeros((0,intervalSize))

    for __, threat in enumerate(olThreats):
        vlModeLog = np.vstack(( threat.lIntervalModeChangeLog , vlModeLog))
        vlRangeLog = np.vstack(( threat.lIntervalZoneAssessmentLog , vlRangeLog))
        vlLethalRangeLog = np.vstack(( threat.lIntervalLethalRangeLog , vlLethalRangeLog))
        vlCoincPercLog = np.vstack(( threat.lIntervalCoincidencePercentageLog , vlCoincPercLog))
        vlJammingLog = np.vstack((threat.lIntervalJammingLog, vlJammingLog))
        vlDetectionLog = np.vstack((threat.lDetectionsInIntervalLog, vlDetectionLog))
        vlCPILog = np.vstack((threat.lTotalCPIsInIntervalLog, vlCPILog))

    resultPath = os.path.join(common.RESULTDIR, interFile)
    if os.path.exists(resultPath):
        os.remove(resultPath + common.RESULTMODESLOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTRANGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTLETHALRANGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTCOINCIDENCEPERCENTAGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTJAMMINGLOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.DETECTIONSLOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.CPILOG + common.RESULTFILEEXT)
    else:
        os.makedirs(resultPath)

    save(resultPath + common.RESULTMODESLOG + common.RESULTFILEEXT, vlModeLog[::-1])
    save(resultPath + common.RESULTRANGELOG + common.RESULTFILEEXT, vlRangeLog[::-1])
    save(resultPath + common.RESULTLETHALRANGELOG + common.RESULTFILEEXT, vlLethalRangeLog[::-1])
    save(resultPath + common.RESULTCOINCIDENCEPERCENTAGELOG + common.RESULTFILEEXT, vlCoincPercLog[::-1])
    save(resultPath + common.RESULTJAMMINGLOG + common.RESULTFILEEXT, vlJammingLog[::-1])
    save(resultPath + common.DETECTIONSLOG + common.RESULTFILEEXT, vlDetectionLog[::,-1])
    save(resultPath + common.CPILOG + common.RESULTFILEEXT, vlCPILog[::,-1])

    shutil.move(r'tij.log', resultPath+'tij.log')

if __name__ == "__main__":
    main(sys.argv[1:])