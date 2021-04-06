import os, getopt, sys, traceback
import threats
import pltf as platform
import jammer
import common
import jsonParser
import visualize
import numpy as np
import intervalProcess as interval
import logging

logging.basicConfig(level = logging.NOTSET)
np.set_printoptions(precision=5, suppress=True)

def argumentExtraction(argv):
    setViz = False

    try:
        [opts, argv] = getopt.getopt(
            argv, "h:v", ["help", "visualize"])
    except getopt.GetoptError:
        helpPrints()
        return None
    for opt, _ in opts:
        if opt == '-h':
            helpPrints()
            exit()
        elif opt in ("-v", "--visualize"):
            setViz = True
            logging.info('Visualization set to True')

    return setViz

def helpPrints():
    logging.info('\npyTIJ.py <arguments> \n')
    logging.info('~~~ARGUMENT LIST~~~\n')
    logging.info('-v:\tvisualize\n')

def main(argv):
    oPlatform = None
    oJammer = None
    olThreats = None
    doViz = False

    doViz = argumentExtraction(argv)

    # Initialize
    [oPlatform, oJammer, olThreats] = initEnvironment()

    interval.intervalProcessor(oPlatform, oJammer, olThreats, oJammer.oChannel)

    # visualize the world
    if doViz:
        # visualize.worldview(cPlatform, cThreatLibrary)
        visualize.topview(oPlatform, olThreats)

    pass

def initEnvironment():
    # init platform class instance
    oPlatform = platform.cPlatform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    olThreats = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))

    oJammer = jammer.cJammer(jsonParser.parseJsonFile(common.JAMMERDIR))

    # profile creator
    for itChannel in oJammer.oChannel:
        itChannel.oInterval = interval.cInterval(itChannel.interval_time_ms, oPlatform.timeStop_ms)

    return [oPlatform, oJammer, olThreats]


if __name__ == "__main__":
    main(sys.argv[1:])