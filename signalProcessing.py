import scipy.special as spspec
import numpy as np
import math
from matplotlib import pyplot as plt
from labellines import labelLine, labelLines

def Pd(Pfa, SNR):
    return 0.5*spspec.erfc(spspec.erfcinv(2*Pfa)-np.sqrt(SNR))

def rocsnr(snrRange, PfaRange, numPoints, integration):
    PfaStep = (PfaRange[1] - PfaRange[0])/numPoints
    
    Pfa = np.arange(PfaRange[0], PfaRange[1], PfaStep)
    PdMatrix = np.zeros((snrRange.__len__(),Pfa.size))
    
    snrPoint = 0
    for snr in snrRange:
        pfaPoint = 0
        for far in Pfa:
            PdMatrix[snrPoint, pfaPoint] = Pd(far, snr)
            pfaPoint = pfaPoint + 1
        plt.plot(Pfa, PdMatrix[snrPoint,:], label=str(snr))
        snrPoint = snrPoint + 1

    labelLines(plt.gca().get_lines(),zorder=2.5)
    PfaXaxisStep = (PfaRange[1] - PfaRange[0])/(numPoints*.02)
    plt.xticks(np.arange(PfaRange[0], PfaRange[1], PfaXaxisStep))
    plt.yticks(np.arange(0,1.0,0.05))
    plt.grid(True)
    plt.show()
    return Pfa, PdMatrix


        
