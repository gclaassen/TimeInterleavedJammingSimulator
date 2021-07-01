import math
import common
import traceback
import logging
import scipy
import scipy.stats
import scipy.special
import numpy as np

#log base enum valuPs
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

def calculatPspreadingLoss(range_m, frequency_MHz):
    return 32 + convertTodB(range_m, 20, BASE10) + convertTodB(frequency_MHz, 20, BASE10)

def calculateWaveLength(velocity_ms, frequency_MHz):
    return velocity_ms/convertFrequency_MHzToHz(frequency_MHz)

def phiInv(x):
    return math.sqrt(2)*scipy.special.erfinv(2*x-1)

def phi(x):
    return 0.5*(1 + scipy.special.erf(x/math.sqrt(2)))

def calculatePd(Pfa, Nsnr, integration):
    if integration == 'CI':
        return 0.5*scipy.special.erfc(scipy.special.erfcinv(2*Pfa)-np.sqrt(Nsnr))

    elif integration == 'NCI':
        NotImplementedError

def calculateSNR(Pd, Pfa, n, integration):
    if integration == 'CI':
        return (1/(2*n))*math.pow(phiInv(Pfa) - phiInv(Pd), 2)

    elif integration == 'NCI':
        NotImplementedError


def radarEquationSNR(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Rc_km, NF, mode, PRI_us):
    # Return the detectability factor (Max SNR for a single detection)

    waveLength = calculateWaveLength(common.c, Fc_MHz)
    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)

    DC = pw_us/PRI_us
    Pt = convertPower_KiloWattToWatt(Pt_kw)
    Pavg = Pt * DC

    CPI = N * convertTime_MicrosecondsToSeconds(PRI_us)

    Rc = convertRange_KilometerToMeter(Rc_km)

    Ft = convertFromdB(common.Ft_dB)
    Fr = convertFromdB(common.Fr_dB)

    La = convertFromdB(common.La_dB)
    Lp = convertFromdB(common.Lp_1D_dB) if mode <= 1 else 1
    La = convertFromdB(common.La_dB*Rc_km)


    Ts = common.kT0*NF

    Ps =  (Pavg * CPI * Gt * Gr * rcs_m2 * math.pow(waveLength,2) * Fr * Ft) / (math.pow(common.STERADIANS, 3) * math.pow(Rc, 4) * La * Lp * La)
    En =  Ts

    SNR = N*Ps/En

    SNR_dB = convertTodB(SNR, 10, BASE10)

    return SNR_dB


def radarEquationRange(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, snr, NF_dB, mode, PRI_us):
    # Return the range value
    waveLength = calculateWaveLength(common.c, Fc_MHz)
    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)

    DC = pw_us/PRI_us
    Pt = convertPower_KiloWattToWatt(Pt_kw)
    Pavg = Pt * DC

    CPI = N * convertTime_MicrosecondsToSeconds(PRI_us)

    Ft = convertFromdB(common.Ft_dB)
    Fr = convertFromdB(common.Fr_dB)

    La = convertFromdB(common.La_dB)
    Lp = convertFromdB(common.Lp_1D_dB) if mode <= 1 else 1

    NF = convertFromdB(NF_dB)

    kTs = common.kT0*NF

    Ps =  (Pavg * CPI * Gt * Gr * rcs_m2 * math.pow(waveLength,2) * Ft * Fr )/ (math.pow(common.STERADIANS, 3) * snr * La * Lp)
    Pn =  kTs 

    Rx_m = math.pow(N*Ps/Pn,(1/4))

    return convertRange_MeterToKiloMeter(Rx_m)


def radarEquationRange_CPIJP(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, snr, Pj_kW, Gj_dB, Bj_MHz, NF_dB, cpiJammingAvg, mode, PRI_us):
    # Return the range value
    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gt_dB)

    waveLength = calculateWaveLength(common.c, Fc_MHz)

    DC = pw_us/PRI_us
    Pt = convertPower_KiloWattToWatt(Pt_kw)
    Pavg = Pt * DC

    CPI = N * convertTime_MicrosecondsToSeconds(PRI_us)

    Ft = convertFromdB(common.Ft_dB)
    Fr = convertFromdB(common.Fr_dB)

    La = convertFromdB(common.La_dB)
    Lp = convertFromdB(common.Lp_1D_dB) if mode <= 1 else 1

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Fjp = convertFromdB(common.Fjp_dB)
    Fjt = convertFromdB(common.Fjt_dB)

    NF = convertFromdB(NF_dB)

    kTs = common.kT0*NF

    Rx_m =  math.pow( (Pavg * CPI * Gt * rcs_m2 * Ft * Fr * (Bj) )/ (common.STERADIANS * snr * La * Lp * (common.Qj * (cpiJammingAvg * Pj) * Gj * Fjt * Fjp )), 1/2)

    return convertRange_MeterToKiloMeter(Rx_m)

def radarEquationSNR_NoiseJamming(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Rc_km, NF_dB, Pj_kW, Gj_dB, Bj_MHz, mode, PRI_us) :
    #  Return the JPP value

    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)

    waveLength = calculateWaveLength(common.c, Fc_MHz)

    DC = pw_us/PRI_us
    Pt = convertPower_KiloWattToWatt(Pt_kw)
    Pavg = Pt * DC

    CPI = N * convertTime_MicrosecondsToSeconds(PRI_us)

    Rc = convertRange_KilometerToMeter(Rc_km)

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Ft = convertFromdB(common.Ft_dB)
    Fr = convertFromdB(common.Fr_dB)

    La = convertFromdB(common.La_dB * Rc_km)
    Lp = convertFromdB(common.Lp_1D_dB) if mode <= 1 else 1

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Fjp = convertFromdB(common.Fjp_dB)
    Fjt = convertFromdB(common.Fjt_dB)

    Lja = convertFromdB(common.Lja_dB * Rc_km)

    NF = convertFromdB(NF_dB)

    Tj = (common.Qj * Pj * Gj * Gr * math.pow(waveLength,2) * Fjt * Fr * Fjp) / (math.pow(common.STERADIANS, 2) * math.pow(Rc, 2) * common.Boltzman_k * Bj * Lja )

    Ts = common.kT0*NF + Tj

    Ps =  Pavg * CPI * Gt * Gr * rcs_m2 * math.pow(waveLength,2) * Ft * Fr / (math.pow(common.STERADIANS, 3) * math.pow(Rc, 4) * La * Lp )
    Pn =  common.Boltzman_k * Ts

    SNR_D0 = Ps/Pn

    SNR_CI = N * SNR_D0

    SNR_dB = convertTodB(SNR_CI, 10, BASE10)

    return SNR_dB

def radarEquationSNR_CPIJP(N, Pt_kw, Gt_dB, Gr_dB, pw_us, rcs_m2, Fc_MHz, Rc_km, NF_dB, Pj_kW, Gj_dB, Bj_MHz, minPd, Pfa, cpiJammingAvg, mode, PRI_us) :
    #  Return the JPP value

    Gt = convertFromdB(Gt_dB)
    Gr = convertFromdB(Gr_dB)

    waveLength = calculateWaveLength(common.c, Fc_MHz)

    DC = pw_us/PRI_us
    Pt = convertPower_KiloWattToWatt(Pt_kw)
    Pavg = Pt * DC

    CPI = N * convertTime_MicrosecondsToSeconds(PRI_us)

    Rc = convertRange_KilometerToMeter(Rc_km)

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Ft = convertFromdB(common.Ft_dB)
    Fr = convertFromdB(common.Fr_dB)

    La = convertFromdB(common.La_dB * Rc_km)
    Lp = convertFromdB(common.Lp_1D_dB) if mode <= 1 else 1

    Pj= convertPower_KiloWattToWatt(Pj_kW)
    Bj = convertFrequency_MHzToHz(Bj_MHz)
    Gj = convertFromdB(Gj_dB)

    Fjp = convertFromdB(common.Fjp_dB)
    Fjt = convertFromdB(common.Fjt_dB)

    Lja = convertFromdB(common.Lja_dB * Rc_km)

    NF = convertFromdB(NF_dB)

    Tj = (common.Qj * Pj * Gj * Gr * math.pow(waveLength,2) * Fjt * Fjp * Fr) / (math.pow(common.STERADIANS, 2) * math.pow(Rc, 2) * common.Boltzman_k * Bj * Lja )

    Tj_ij = cpiJammingAvg * Tj

    Ts = common.kT0*NF + Tj_ij

    Ps =  (Pavg * CPI * Gt * Gr * rcs_m2 * math.pow(waveLength,2) * Ft * Fr)/(math.pow(common.STERADIANS, 3) * math.pow(Rc, 4) * La * Lp )
    Pn =  Ts

    SNR = Ps/Pn

    SNR_CI = N*SNR

    SNR_dB = convertTodB(SNR, 10, BASE10)
    SNR_CI_db = convertTodB(SNR_CI, 10, BASE10)

    PdCurrent = calculatePd(Pfa, SNR_CI, 'CI')

    if(PdCurrent >= minPd):
        return [False, SNR_CI_db, PdCurrent]
    else:
        return [True, SNR_CI_db, PdCurrent]