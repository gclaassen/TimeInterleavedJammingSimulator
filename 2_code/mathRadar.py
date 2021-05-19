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
    return numTime_us*math.pow(10,-6)

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
    return frequency_MHz*math.pow(10, 6)

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

def radarEquation_DetectabilityFactor_dB(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Rc_km):
    # Return the detectability factor (Max SNR for a single detection)

    Pt = convertPower_KiloWattToWatt(Pt_kw)
    pw = convertTime_MicrosecondsToSeconds(pw_us)
    Rc = convertRange_KilometerToMeter(Rc_km)

    N_dB = convertTodB(N, 10, BASE10)
    Pt_dBW = convertTodB(Pt, 10, BASE10)
    rcs_dBsm = convertTodB(rcs_m2, 10, BASE10)
    constants_dB = convertTodB(common.STERADIANS, 30, BASE10)
    pw_dB = convertTodB(pw, 10, BASE10)
    waveLength_dBm = convertTodB(calculateWaveLength(common.c, Fc_MHz), 20, BASE10)
    Rc_dBm = convertTodB(Rc, 40, BASE10)

    return (N_dB + Pt_dBW + pw_dB + Gt_dB + Gr_dB + rcs_dBsm + waveLength_dBm + common.F_dB) - (constants_dB + common.kT0_dB + Rc_dBm + common.L_dB)


def radarEquation_DetectabilityFactor(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Rc_km):
    # Return the detectability factor (Max SNR for a single detection)

    waveLength = calculateWaveLength(common.c, Fc_MHz)
    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)

    Pt = convertPower_KiloWattToWatt(Pt_kw)
    pw = convertTime_MicrosecondsToSeconds(pw_us)
    Rc = convertRange_KilometerToMeter(Rc_km)

    Fp = convertFromdB(common.Fp_dB)
    Frdr = convertFromdB(common.Frdr_dB)
    Flens = convertFromdB(common.Flens_dB)

    La = convertFromdB(common.La_dB)
    Lt = convertFromdB(common.Lt_dB)

    Ts = common.kT0

    Es =  N * Pt * pw * Gt * Gr * rcs_m2 * math.pow(waveLength,2) * Fp * Frdr * Flens
    En =  math.pow(common.STERADIANS, 3) * Ts * math.pow(Rc, 4) * La * Lt

    SNR = Es/En
    SNR_dB = convertTodB(SNR, 10, BASE10)
    return SNR_dB

def radarEquation_Range(Pt_Kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Ts_K, Dx_dB, Lt_dBm, La_dBm):
    # Return the range value
    return math.pow(common.RadarEquationConstant * (( convertPower_KiloWattToWatt(Pt_Kw) * pw_us * Gt_dB * Gr_dB * rcs_m2 )/( math.pow(Fc_MHz,2) * Ts_K * Dx_dB * La_dBm * Lt_dBm )), 1/4)


def radarEquation_SSJamming_DetectabilityFactor(N, Pt_kw, Gt_dB, pw_us, rcs_m2, Rc_km, Pj_kW, Gj_dB, Bj_MHz) :
    # Return the detectability factor (Max SNR for a single detection)

    Gt = convertFromdB(Gt_dB)

    Pt = convertPower_KiloWattToWatt(Pt_kw)
    pw = convertTime_MicrosecondsToSeconds(pw_us)
    Rc = convertRange_KilometerToMeter(Rc_km)

    Fp = convertFromdB(common.Fp_dB)
    Frdr = convertFromdB(common.Frdr_dB)
    Flens = convertFromdB(common.Flens_dB)

    La = convertFromdB(common.La_dB)
    Lt = convertFromdB(common.Lt_dB)

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Fjl = convertFromdB(common.Fjl_dB)
    Fjp = convertFromdB(common.Fjp_dB)
    Lja = convertFromdB(common.Lja_dB)
    Ljt = convertFromdB(common.Ljt_dB)

    Es =  N * Pt * pw * Gt * rcs_m2 * Fp * Frdr * Flens * Bj * Lja * Ljt
    En =  common.STERADIANS * math.pow(Rc, 2) * La * Lt * (common.Qj * Pj * Gj * Fjl * Fjp )

    SNR = Es/En
    SNR_dB = convertTodB(SNR, 10, BASE10)

    return SNR_dB

def radarEquation_SSJamming_JPP(N, Pt_kw, Gt_dB, pw_us, rcs_m2, Rc_km, Pj_kW, Gj_dB, Bj_MHz, snrReq, cpiJammingAvg) :
    #  Return the JPP value

    Gt = convertFromdB(Gt_dB)

    Pt = convertPower_KiloWattToWatt(Pt_kw)
    pw = convertTime_MicrosecondsToSeconds(pw_us)
    Rc = convertRange_KilometerToMeter(Rc_km)

    Fp = convertFromdB(common.Fp_dB)
    Frdr = convertFromdB(common.Frdr_dB)
    Flens = convertFromdB(common.Flens_dB)

    La = convertFromdB(common.La_dB)
    Lt = convertFromdB(common.Lt_dB)

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Fjl = convertFromdB(common.Fjl_dB)
    Fjp = convertFromdB(common.Fjp_dB)
    Lja = convertFromdB(common.Lja_dB)
    Ljt = convertFromdB(common.Ljt_dB)

    Es =  N * Pt * pw * Gt * rcs_m2 * Fp * Frdr * Flens * Bj * Lja * Ljt
    En =  common.STERADIANS * math.pow(Rc, 2) * La * Lt * ((cpiJammingAvg) * (common.Qj * Pj * Gj * Fjl * Fjp ))

    SNR = Es/En
    SNR_dB = convertTodB(SNR, 10, BASE10)

    JsrAvg = SNR_dB/snrReq

    if(JsrAvg >= 1.0):
        return False
    else:
        return True