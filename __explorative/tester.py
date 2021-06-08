import numpy as np
import signalProcessing as signal
import math

snrRange = [-2, 2, 3, 4]
PfaRange = [1e-10, 1]
numPoints = 101
integration = 'CI'
pulsesForIntegration = 1

Pfa = math.pow(10,-6)
# Pfa = 0.01
snr_dB = 10
Pd = 0.25

numSnr = signal.calculateSNR(Pd, Pfa, pulsesForIntegration)
numSnr_dB = 10*math.log10(numSnr)

numPd = signal.calculatePd(Pfa, snr_dB, pulsesForIntegration, integration)

snrMatrix = signal.albersheimsSnr([0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99], 1e-6, [1, 4, 8, 16, 32, 64, 128])

# [Pfa,Pd] = signal.rocsnr(snrRange, PfaRange, pulsesForIntegration, numPoints, integration)
# signal.rocSNRplot(snrRange, Pd, Pfa, pulsesForIntegration, integration)

pass