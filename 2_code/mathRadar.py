import math
import common
import traceback
import logging

#log base enum values
BASENORMAL          = 0 # log()
BASE10              = 1 # log10()


def convertTodBm(numValue, numMultiplier, enumBase):
    if(enumBase == BASE10):
        return numMultiplier*math.log10(numValue)
    elif(enumBase == BASENORMAL):
        return numMultiplier*math.log(numValue)
    else:
        logging.critical('Incorrect log base chosen')

def convertKilometerToMeter(numDistance_km):
    return numDistance_km*1e3

def convertMeterToKiloMeter(numDistance_m):
    return numDistance_m*1e-3

def convertTimeSecondsToMicroseconds(numTime_s):
    return numTime_s*1e6

def convertTimeMilisecondsToMicroseconds(numTime_ms):
    return numTime_ms*1e3

def convertTimeMicrosecondsToMilliseconds(numTime_us):
    return numTime_us*1e-3

def convertTimeMicrosecondsToSeconds(numTime_us):
    return numTime_us*1e-6

def convertErpdBm(numPower_W, numGain):
    return convertPowerWattTodBm(numPower_W) + convertGaindBm(numGain)

def convertPowerWattTodBm(numPower_W):
    return (convertTodBm(numPower_W,10, BASE10) + 30)

def convertPowerdBmToWatt(numPower_dBm):
    x = math.pow(numPower_dBm/10, 10)
    return (1*x)/1000

def convertGaindBm(numGain):
    return convertTodBm(numGain,10, BASE10)

def convertPRFtoPRIus(numPRF_Hz, numPW_us):
    return ((1/(numPRF_Hz))*1e6) - numPW_us

def convertPeakPowerToAvgPower(numPeakPower_W, numDutyCycle):
    return numPeakPower_W*numDutyCycle

def calculateDutyCycle(numPW_us, numPRI_us):
    return numPW_us/numPRI_us

def calculateErpW(numPower, numGain):
    return numPower*numGain

def attenuation(numWavelength, numRc):
    return ((common.STERADIANS*numRc)/numWavelength) ^ 2

def calculateSpreadingLoss(range_m, wavelength):
    # return 32 + convertTodBm(range_m, 20, BASE10)
    NotImplementedError

def radarEquation_DetectabilityFactor(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, R_km, Lt_dBm, La_dBm):
    # Return the detectability factor (Max SNR for a single detection)
    return common.RadarEquationConstant * (( Pt_Kw * pw_us * Gt_dB * Gr_dB * rcs_m2 )/( math.pow(Fc_MHz,2) * Ts_K * math.pow(R_km,4) * La_dBm * Lt_dBm ))

def radarEquation_Range(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, Dx_dB, Lt_dBm, La_dBm):
    # Return the range value
    return math.pow(common.RadarEquationConstant * (( Pt_Kw * pw_us * Gt_dB * Gr_dB * rcs_m2 )/( math.pow(Fc_MHz,2) * Ts_K * Dx_dB * La_dBm * Lt_dBm )), 1/4)


## TODO: rework
# def attenuation_dB(numWavelength_MHz, numRc_m):
#     return -27.55 + convertTodBm(numRc_m, 20, BASE10) + convertTodBm(numWavelength_MHz, 20, BASE10)

## TODO: rework
# def platformSkinReturnPower_dB(ERPt_dB, Fc_MHz,  Gr_dB, rcs_m2, R_km, Lr_dBm):
#     return ( ERPt_dB - 103 - convertTodBm(Fc_MHz, 20, BASE10) - convertTodBm(R_km, 40, BASE10) + Gr_dB + convertTodBm(rcs_m, 10, BASE10)  + Lr_dBm )