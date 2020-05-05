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
        snrPoint = snrPoint + 1
    return Pfa, PdMatrix

def rocSNRplot(snrRange, Pd, Pfa):
    snrPoint = 0
    for snr in snrRange:
            plt.semilogx(Pfa, Pd[snrPoint,:], label=str(snr))
            snrPoint = snrPoint + 1

    labelLines(plt.gca().get_lines(),zorder=2.5)
    plt.title('Receiver Operating Characteristics (ROC) Curves')
    plt.ylabel('Probability of Detection')
    plt.xlabel('Probability of False Alarm')
    plt.xticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    plt.yticks([0, 0.1, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.87, 0.9, 0.93, 0.95, 0.98, 1])
    plt.grid(True)
    plt.show()
    
# def rocPFAplot(snrRange, Pd, Pfa, reqPfa):
    
