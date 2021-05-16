import math
import common
import traceback
import logging

#log base enum values
BASENORMAL          = 0 # log()
BASE10              = 1 # log10()


def convertTodB(numValue, numMultiplier, enumBase):
    if(enumBase == BASE10):
        return numMultiplier*math.log10(numValue)
    elif(enumBase == BASENORMAL):
        return numMultiplier*math.log(numValue)
    else:
        logging.critical('Incorrect log base chosen')

def convertFromdB(numValue):
    return math.pow(10, (numValue/10))

def convertRange_KilometerToMeter(numDistance_km):
    return numDistance_km*1e3

def convertRange_MeterToKiloMeter(numDistance_m):
    return numDistance_m*1e-3

def convertTime_SecondsToMicroseconds(numTime_s):
    return numTime_s*1e6

def convertTime_MilisecondsToMicroseconds(numTime_ms):
    return numTime_ms*1e3

def convertTime_MicrosecondsToMilliseconds(numTime_us):
    return numTime_us*1e-3

def convertTime_MicrosecondsToSeconds(numTime_us):
    return numTime_us*1e-6

def convertPower_ErpTodBm(numPower_W, numGain_dB):
    return convertPower_WattTodBm(numPower_W) + numGain_dB

def convertPower_WattTodBm(numPower_W):
    return (convertTodB(numPower_W,10, BASE10) + 30)

def convertPower_dBmToWatt(numPower_dBm):
    x = math.pow(numPower_dBm/10, 10)
    return (1*x)/1000

def convertPower_KiloWattToWatt(numPower_kW):
    return numPower_kW*1e3

def convertGaindBm(numGain):
    return convertTodB(numGain,10, BASE10)

def convertPRFtoPRIus(numPRF_Hz, numPW_us):
    return ((1/(numPRF_Hz))*1e6) - numPW_us

def convertPeakPowerToAvgPower(numPeakPower_W, numDutyCycle):
    return numPeakPower_W*numDutyCycle

def convertFrequency_MHzToHz(frequency_MHz):
    return frequency_MHz*1e6

def calculateDutyCycle(numPW_us, numPRI_us):
    return numPW_us/numPRI_us

def calculateErpW(numPower, numGain):
    return numPower*numGain

def attenuation(numWavelength, numRc):
    return ((common.STERADIANS*numRc)/numWavelength) ^ 2

def calculateSpreadingLoss(range_m, frequency_MHz):
    return 32 + convertTodB(range_m, 20, BASE10) + convertTodB(frequency_MHz, 20, BASE10)

def calculateWaveLength(velocity_ms, frequency_MHz):
    return velocity_ms/convertFrequency_MHzToHz(frequency_MHz)

def radarEquation_DetectabilityFactor_dB(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_dB, R_km, Lt_dBm, La_dBm):
    # Return the detectability factor (Max SNR for a single detection)

    Pt_dB = convertPower_WattTodBm(convertPower_KiloWattToWatt(Pt_Kw))
    rcs_dB = convertTodB(rcs_m2, 10, BASE10)
    constants_dB = -38.2
    # pw_dB = convertTodB(convertTime_MicrosecondsToSeconds(pw_us), 10, BASE10)
    # fc_dB = convertTodB(convertFrequency_MHzToHz(Fc_MHz), 20, BASE10)
    # R_dB = convertTodB(convertRange_KilometerToMeter(R_km), 40, BASE10)

    pw_dB = convertTodB(pw_us, 10, BASE10)
    fc_dB = convertTodB(Fc_MHz, 20, BASE10)
    R_dB = convertTodB(R_km, 40, BASE10)

    return constants_dB + Pt_dB + pw_dB + Gt_dB + Gr_dB + rcs_dB - fc_dB - Ts_dB - R_dB - Lt_dBm - La_dBm


def radarEquation_DetectabilityFactor(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, R_km, Lt_dBm, La_dBm, Cb):
    # Return the detectability factor (Max SNR for a single detection)

    waveLength = calculateWaveLength(common.c, Fc_MHz)
    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)
    Lt = convertFromdB(Lt_dBm)
    La = convertFromdB(La_dBm)

    return convertTodB( (( N * Pt_kw * pw_us * Gt * Gr * rcs_m2 + math.pow(waveLength,2) )/( math.pow(4*math.pi, 3) * Ts_K * math.pow(R_km, 4) * Cb * Lt * La )), 10, BASE10)


def radarEquation_Range(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, Dx_dB, Lt_dBm, La_dBm):
    # Return the range value
    return math.pow(common.RadarEquationConstant * (( convertPower_KiloWattToWatt(Pt_Kw) * pw_us * Gt_dB * Gr_dB * rcs_m2 )/( math.pow(Fc_MHz,2) * Ts_K * Dx_dB * La_dBm * Lt_dBm )), 1/4)


## TODO: rework
# def attenuation_dB(numWavelength_MHz, numRc_m):
#     return -27.55 + convertTodBm(numRc_m, 20, BASE10) + convertTodBm(numWavelength_MHz, 20, BASE10)

## TODO: rework
# def platformSkinReturnPower_dB(ERPt_dB, Fc_MHz,  Gr_dB, rcs_m2, R_km, Lr_dBm):
#     return ( ERPt_dB - 103 - convertTodBm(Fc_MHz, 20, BASE10) - convertTodBm(R_km, 40, BASE10) + Gr_dB + convertTodBm(rcs_m, 10, BASE10)  + Lr_dBm )


def radarEquation_SSJamming_DetectabilityFactor_dB(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, R_km, Lt_dBm, La_dBm, Pj_kW, Gj_dB, Bj_MHz ):
    # Return the detectability factor when jamming is active (Max SNR for a single detection)

    Pt_dB = convertTodB(convertPower_KiloWattToWatt(Pt_Kw), 10, BASE10)
    pw_dB = convertTodB(convertTime_MicrosecondsToSeconds(pw_us), 10, BASE10)
    waveLength_dB = convertTodB(calculateWaveLength(common.c, Fc_MHz), 20, BASE10)
    rcs_dB = convertTodB(rcs_m2, 10, BASE10)
    constants_dB = convertTodB((4*math.pi), 10, BASE10)
    R_dB = convertTodB(convertRange_KilometerToMeter(R_km), 20, 
    BASE10)

    Pj_dB = convertTodB(convertPower_KiloWattToWatt(Pj_kW), 10, BASE10)
    Bj_dB = convertTodB(convertFrequency_MHzToHz(Bj_MHz), 10, BASE10)

    Wj_dB = (Pj_dB + Gj_dB) - (Bj_dB)

    return (Pt_dB + pw_dB + Gt_dB + Gr_dB + waveLength_dB + rcs_dB) - (constants_dB + R_dB + Lt_dBm + La_dBm + Wj_dB)


def radarEquation_SSJamming_DetectabilityFactor(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, R_km, Lt_dBm, La_dBm, Cb, Pj_kW, Gj_dB, Bj_MHz) :
    # Return the detectability factor (Max SNR for a single detection)

    Gt = convertFromdB(Gt_dB)
    Gj = convertFromdB(Gj_dB)
    Lt = convertFromdB(Lt_dBm)
    La = convertFromdB(La_dBm)
    Wj = convertPower_KiloWattToWatt(Pj_kW)/ Bj_MHz #W/MHz

    return convertTodB(( N * Pt_kw * pw_us ) * (( Gt * rcs_m2 )/(4*math.pi * math.pow(R_km, 2) * Cb * Lt * La * Wj * Gj )), 10, BASE10)

