import scipy.special as spspec
import numpy as np
import math
from matplotlib import pyplot as plt
from labellines import labelLine, labelLines
import spectrum
from scipy.stats import ncx2

def Pd(Pfa, SNR, N, integration):
    if integration is 'CI':
        return 0.5*spspec.erfc(spspec.erfcinv(2*Pfa)-np.sqrt(SNR*N))
    elif integration is 'NCI':
        Threshold = np.real(spspec.gammainccinv(1-Pfa, N))
        Sqrt2Threshold = math.sqrt(2*Threshold)
        
        NX = N*SNR
        NXT = NX*Threshold
        
        # Pd = spspec.
        

def rocsnr(snrRange, PfaRange, numPulses, numPoints, integration):
    minPfa = math.log10(PfaRange[0])
    maxPfa = math.log10(PfaRange[1])
    
    PfaStep = (maxPfa - minPfa)/numPoints
    Pfa = np.logspace(minPfa, maxPfa, numPoints)
    PdMatrix = np.zeros((snrRange.__len__(),Pfa.size))
    
    snrPoint = 0
    for snr in snrRange:
        snrPow = spectrum.db2pow(snr)
        pfaPoint = 0
        for far in Pfa:
            PdMatrix[snrPoint, pfaPoint] = Pd(far, snrPow, numPulses, integration)
            pfaPoint = pfaPoint + 1
        plt.plot(Pfa, PdMatrix[snrPoint,:], label=str(snr))
        snrPoint = snrPoint + 1

    labelLines(plt.gca().get_lines(),zorder=2.5)
    PfaXaxisStep = (maxPfa - minPfa)/numPoints*0.02
    # plt.xticks(np.arange(PfaRange[0], PfaRange[1], PfaXaxisStep))
    plt.xticks([1e-10, 1e-6, 1e-3, 1], ['1e-10', '1e-6', '1e-3', '1'])
    plt.yticks([0, 0.1, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.87, 0.9, 0.91, 0.93, 0.95, 0.97, 0.99, 1])
    plt.grid(True)
    plt.show()
    return Pfa, PdMatrix