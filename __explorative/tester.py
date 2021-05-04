import numpy as np
import signalProcessing as signal

snrRange = [-2, 2, 3, 4]
PfaRange = [1e-10, 1]
numPoints = 101
integration = 'NCI'
pulsesForIntegration = 1

snrMatrix = signal.albersheimsSnr([0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99], 1e-6, [1, 4, 8, 16, 32, 64, 128])

# [Pfa,Pd] = signal.rocsnr(snrRange, PfaRange, pulsesForIntegration, numPoints, integration)
# signal.rocSNRplot(snrRange, Pd, Pfa, pulsesForIntegration, integration)

pass