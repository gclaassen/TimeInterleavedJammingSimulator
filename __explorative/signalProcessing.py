import scipy.special as sp_spec
import numpy as np
import math
from matplotlib import pyplot as plt
from labellines import labelLine, labelLines
import spectrum
import scipy.stats as sp_stats


# PULSE INTEGRATION
def Pd(Pfa, SNR, N, integration):
    if integration == 'CI':
        return 0.5*sp_spec.erfc(sp_spec.erfcinv(2*Pfa)-np.sqrt(SNR*N))
    elif integration == 'NCI':
    #     T = -np.log(Pfa)
    #     T = np.real(sp_spec.gammaincinv(1-Pfa,N))
    #     Nx = N*SNR
    #     marcumVal = 0.5*sp_spec.erfc(np.sqrt(2*Nx), np.sqrt(2*T))
    #     expVal = np.exp(-(T+Nx))
    #     sumBesselVal = 0
    #     pulseRange = np.arange(2, N, 1)
    #     for r in pulseRange:
    #         sumBesselValTemp = np.power(T/Nx,(r-1)/2)*sp_spec.jv(r-1 , 2*np.sqrt(Nx*T))
    #         sumBesselVal = sum([sumBesselVal,sumBesselValTemp])
    #     return marcumVal + expVal * sumBesselVal
    # elif integration is 'NCI_ALB':
        # Albersheims Equation Estimation
        return albersheimsPd(spectrum.pow2db(SNR), Pfa, N)

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

def rocSNRplot(snrRange, Pd, Pfa, NumPulses, integration):
    snrPoint = 0
    for snr in snrRange:
        snrLabel = str(snr)+'dB'
        plt.semilogx(Pfa, Pd[snrPoint,:], label=str(snrLabel))
        snrPoint = snrPoint + 1

    labelLines(plt.gca().get_lines(), zorder = 2.5)
    # if(integration == 'CI'):
    #     plt.title('Receiver Operating Characteristics (ROC) Curves for Coherent Integration of ' + str(NumPulses) + ' pulses')
    # elif(integration == 'NCI'):
    #     plt.title('Receiver Operating Characteristics (ROC) Curves for Non-Coherent Integration of ' + str(NumPulses) + ' pulses')
    plt.ylabel('Probability of Detection')
    plt.xlabel('Probability of False Alarm')
    plt.xticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    plt.yticks([0, 0.1, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.87, 0.9, 0.93, 0.95, 0.98, 1])
    plt.grid(True)
    plt.rc('font', size=22)          # controls default text sizes
    plt.show()

# def rocPFAplot(snrRange, Pd, Pfa, reqPfa):


def Rayleigh(mean, stdev):
    plt.figure()
    x = np.linspace(sp_stats.norm.ppf(0.000001), sp_stats.norm.ppf(0.999999999), 1000)

    plt.plot(x, sp_stats.norm.pdf(mean, stdev, x))
    plt.grid(True)
    plt.show()

def NCI_Detection(thresholdRange, noiseStdev, signalAmplitude):
    nciMatrix = np.zeros((3,np.size(thresholdRange)))
    
    nciMatrix[0,:] = np.array(thresholdRange)
    nciMatrix[1,:] = np.array(0.5*(1-sp_spec.erf(thresholdRange/(np.sqrt(2)*noiseStdev))))
    nciMatrix[2,:]= np.array(0.5*(1-sp_spec.erf((thresholdRange-signalAmplitude)/(np.sqrt(2)*noiseStdev))))
    plt.semilogx(nciMatrix[1,:], nciMatrix[2,:], label=str(signalAmplitude))
    plt.grid(True)
    plt.show()
    
    return nciMatrix

def albersheimsSnr(Pd, Pfa, N):
    A = np.log(0.62/Pfa)
    B = np.log(Pd/(1-Pd))
    return -5 * np.log10(N) + (6.2 + (4.54/(np.sqrt(N + 0.44)))) * np.log10(A + 0.12 * A * B + 1.7* B)

def albersheimsSnr(PdRange, Pfa, N):
    SnrMatrix = np.zeros((PdRange.__len__(),1+N.__len__() ))
    for PdIdx, Pd in enumerate(PdRange):
        A = np.log(0.62/Pfa)
        B = np.log(Pd/(1-Pd))
        SnrMatrix[PdIdx, 0] = Pd
        for Nidx, cpi in enumerate(N):
            idx = Nidx + 1
            SnrMatrix[PdIdx, idx] = -5 * np.log10(cpi) + (6.2 + (4.54/(np.sqrt(cpi + 0.44)))) * np.log10(A + 0.12 * A * B + 1.7* B)
        

    return SnrMatrix

def albersheimsPd(x, Pfa, N):
    A = np.log(0.62/Pfa)
    Z = (x + 5 * np.log10(N))/(6.2 + (4.54/(np.sqrt(N + 0.44))))
    B = (np.power(10,Z) - A)/(1.7 + 0.12 * A)
    return (1)/(1 + np.exp(-B))