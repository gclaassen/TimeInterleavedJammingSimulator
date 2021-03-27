from numba import cuda
import numpy
import math

class cInterval:
    total_intervals: int = 0
    current_interval: int = 0
    current_interval_Tstart: float = 0
    current_interval_Tstop: float = 0
    pulse_profile = None
    jammer_profile = None

    def __init__(self, numIntervalLength_ms, numFlightTime_ms):
        self.total_intervals = intervalsInFlight_ms(numIntervalLength_ms, numFlightTime_ms)

def intervalsInFlight_ms(numIntervalLength_ms, numFlightTime_ms):
    return math.ceil(numFlightTime_ms/numIntervalLength_ms)

def intervalCoincidenceCalculator(threats, interval):
    pass