import os, getopt, sys
import threats
import plf
import common
import jsonParser
import visualize
import signalProcessing as signal

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
    pf = plf.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    th = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))
    
    # visualize the world
    if(doViz == True):
        visualize.worldview(pf, th)

    # snrRange = [4, 8, 10, 11, 12, 13, 15]
    snrRange = [3, 6, 9, 12]
    PfaRange = [1e-10, 1]
    numPoints = 101
    integration = 'CI'
    totalPulses = 1
    [Pfa,Pd] = signal.rocsnr(snrRange, PfaRange, totalPulses, numPoints, integration)
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
