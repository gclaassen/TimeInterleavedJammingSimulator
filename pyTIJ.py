import os, getopt, sys
import threats
import plf
import common
import jsonParser
import visualize
import signalProcessing as signal
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
    pf = plf.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    th = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))
    
    # visualize the world
    if(doViz == True):
        visualize.worldview(pf, th)
        
    signal.Rayleigh(0,1)

<<<<<<< HEAD
    # snrRange = [1, 2, 4, 8, 12, 16, 20]
    # PfaRange = [1e-9, 1e-3]
    # numPoints = 1001
    # intergration = 0
    # Pd = signal.rocsnr(snrRange, PfaRange, numPoints, intergration)
=======
    snrRange = [-5, -3, -1, 0, 3, 5]
    PfaRange = [1e-10, 1]
    numPoints = 101
    integration = 'CI'
    pulsesForIntegration = 16
    [Pfa,Pd] = signal.rocsnr(snrRange, PfaRange, pulsesForIntegration, numPoints, integration)
    # signal.rocPFAplot(snrRange, Pd, Pfa, 1e-6)
    signal.rocSNRplot(snrRange, Pd, Pfa, pulsesForIntegration, integration)
    alberSnr = signal.albersheimsSnr(0.95, 10e-6, pulsesForIntegration)
>>>>>>> 7d1d3cad8396c69ecf25ecc0e02df05a51029770

    # thresholdRange = np.linspace(0,5,50)
    # noiseStdev = 1
    # signalAmplitude = 1
    # nciMatrix = signal.NCI_Detection(thresholdRange, noiseStdev, signalAmplitude)
    pass


if __name__ == "__main__":
    main(sys.argv[1:])
