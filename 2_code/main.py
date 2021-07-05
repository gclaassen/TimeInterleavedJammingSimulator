import os, getopt, sys, traceback
import threats
import pltf as platform
import jammer
import common
import jsonParser
# import visualize
import numpy as np
import intervalProcess as interval
import logging
import tij
# save numpy array as npy file
from numpy import asarray
from numpy import save

# logging.basicConfig(level = logging.DEBUG)
# comment to print to console, uncomment to save to log file
logging.basicConfig(filename='tij.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S', level = logging.DEBUG)
np.set_printoptions(precision=5, suppress=True)

def argumentExtraction(argv):
    setViz = False
    interFile = None

    try:
        [opts, argv] = getopt.getopt(
            argv, "hv:i:", ["help", "visualize, intermediaryDirectory="])
    except getopt.GetoptError:
        helpPrints()
        return None
    for opt, arg in opts:
        if opt == '-h':
            helpPrints()
            exit()
        elif opt in ("-v", "--visualize"):
            setViz = True
            logging.info('Visualization set to True')
        elif opt in ("-i", "--intermediaryDirectory"):
            interFile = arg + '/'
            logging.info('Intermediary File: {0}'.format(interFile))

    return [interFile, setViz]

def helpPrints():
    logging.info('\npyTIJ.py <arguments> \n')
    logging.info('~~~ARGUMENT LIST~~~\n')
    logging.info('-v:\tvisualize\n')
    logging.info('-i:\tintermediary directory\n')

def main(argv):
    doViz = False
    interFile = None

    [interFile, doViz] = argumentExtraction(argv)

    # Initialize
    [oPlatform, oJammer, olThreats] = initEnvironment(interFile)

    initThreatsForTij(olThreats, oJammer)

    #! Single jamming channel
    interval.intervalProcessorSingleChannel(oPlatform, oJammer, olThreats, oJammer.oChannel[0])
    # save data
    saveThreatData(olThreats, interFile, oJammer.oChannel[0].oInterval.intervals_total)

    #! TODO: Multiple jamming channels
    #     logging.info("Number of processors: %s", mp.Pool(mp.cpu_count()))
    # retList = mp.Pool(oChannel.__len__()).map(interval.intervalProcessor, [oPlatform, oJammer, olThreats, oJammer.oChannel])

    #! visualize the world
    # if doViz:
        # visualize.worldview(cPlatform, cThreatLibrary)
        # visualize.topview(oPlatform, olThreats)

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

    for __, threat in enumerate(olThreats):
        vlModeLog = np.vstack(( threat.lIntervalModeChangeLog , vlModeLog))
        vlRangeLog = np.vstack(( threat.lIntervalZoneAssessmentLog , vlRangeLog))
        vlLethalRangeLog = np.vstack(( threat.lIntervalLethalRangeLog , vlLethalRangeLog))
        vlCoincPercLog = np.vstack(( threat.lIntervalCoincidencePercentageLog , vlCoincPercLog))
        vlJammingLog = np.vstack((threat.lIntervalJammingLog, vlJammingLog))

    resultPath = os.path.join(common.RESULTDIR, interFile)
    if os.path.exists(resultPath):
        os.remove(resultPath + common.RESULTMODESLOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTRANGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTLETHALRANGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTCOINCIDENCEPERCENTAGELOG + common.RESULTFILEEXT)
        os.remove(resultPath + common.RESULTJAMMINGLOG + common.RESULTFILEEXT)
    else:
        os.makedirs(resultPath)

    save(resultPath + common.RESULTMODESLOG + common.RESULTFILEEXT, vlModeLog[::-1])
    save(resultPath + common.RESULTRANGELOG + common.RESULTFILEEXT, vlRangeLog[::-1])
    save(resultPath + common.RESULTLETHALRANGELOG + common.RESULTFILEEXT, vlLethalRangeLog[::-1])
    save(resultPath + common.RESULTCOINCIDENCEPERCENTAGELOG + common.RESULTFILEEXT, vlCoincPercLog[::-1])
    save(resultPath + common.RESULTJAMMINGLOG + common.RESULTFILEEXT, vlJammingLog[::-1])

if __name__ == "__main__":
    main(sys.argv[1:])