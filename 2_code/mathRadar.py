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

def convertTimeKilometreToMetre(numDistance_km):
    return numDistance_km*1e-3

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

def calculateErpW(numPower, numGain):
    return numPower*numGain

def attenuation(numWavelength, numRc):
    return ((common.STERADIANS*numRc)/numWavelength) ^ 2

def attenuation_dB(numWavelength_MHz, numRc_m):
    return -27.55 + convertTodBm(numRc_m, 20, BASE10) + convertTodBm(numWavelength_MHz, 20, BASE10)

def platformSkinReturnPower_dB(numThreat_Tx_ERP, numThreat_Tx_Fc,  numThreat_Rx_GaindBm, numPlatform_RCS, numRange, numRange_losses):
    return ( numThreat_Tx_ERP - 103 - convertTodBm(numThreat_Tx_Fc, 20, BASE10) - convertTodBm(numRange, 40, BASE10) + numThreat_Rx_GaindBm + convertTodBm(numPlatform_RCS, 10, BASE10)  + convertTodBm(numRange_losses, 20, BASE10) )

def friis_dB(ERPt, range, waveform, losses):
    raise NotImplementedError