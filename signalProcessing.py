import scipy.special as spspec
import numpy as np
import math
from matplotlib import pyplot as plt

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
        plt.plot(Pfa, PdMatrix[snrPoint,:])
        snrPoint = snrPoint + 1


    return PdMatrix


        
