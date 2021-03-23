import os, getopt, sys, traceback
import threats
import pltf as platform
import jammer
import common
import jsonParser
import visualize
import numpy as np

def argumentExtraction(argv):
    setViz = False

    try:
        [opts, argv] = getopt.getopt(
            argv, "h:v", ["help", "visualize"])
    except getopt.GetoptError:
        helpPrints()
        return None
    for opt, arg in opts:
        if opt == '-h':
            helpPrints()
            exit()
        elif opt in ("-v", "--visualize"):
            setViz = True
            print('Visualization set to True')

    return setViz

def helpPrints():
    print('\npyTIJ.py <arguments> \n')
    print('~~~ARGUMENT LIST~~~\n')
    print('-v:\tvisualize\n')

def main(argv):

    doViz = False
    
    doViz = argumentExtraction(argv)
    
    # Initialize
    # init platform class instance
    oPlatform = platform.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    oThreats = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))
    
    oJammer = jammer.Jammer(jsonParser.parseJsonFile(common.JAMMERDIR))
    
    # profile creator
    
    
    # visualize the world
    if doViz:
        # visualize.worldview(cPlatform, cThreatLibrary)
        visualize.topview(oPlatform, oThreats)
    

    pass


if __name__ == "__main__":
    main(sys.argv[1:])
    
