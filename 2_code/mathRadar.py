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

def calculateErpW(numPower, numGain):
    return numPower*numGain

def convertTimeSecondsToNanoseconds(numTime_s):
    return numTime_s*1e9

def convertTimeMinutesToSeconds(numTime_m):
    return numTime_m*60

def convertErpdBm(numPower_W, numGain):
    return convertPowerWattTodBm(numPower_W) + convertGaindBm(numGain)

def convertPowerWattTodBm(numPower_W):
    return (convertTodBm(numPower_W,10, BASE10) + 30)

def convertPowerdBmToWatt(numPower_dBm):
    x = math.pow(numPower_dBm/10, 10)
    return (1*x)/1000

def convertGaindBm(numGain):
    return convertTodBm(numGain,10, BASE10)

def attenuation(numWavelength, numRc):
    return ((common.STERADIANS*numRc)/numWavelength) ^ 2

def attenuation_dB(numWavelength_MHz, numRc_m):
    return -27.55 + convertTodBm(numRc_m, 20, BASE10) + convertTodBm(numWavelength_MHz, 20, BASE10)

def platformSkinReturnPower_dB(numThreat_Tx_ERP, numThreat_Tx_Fc,  numThreat_Rx_GaindBm, numPlatform_RCS, numRange, numRange_losses):
    return ( numThreat_Tx_ERP - 103 - convertTodBm(numThreat_Tx_Fc, 20, BASE10) - convertTodBm(numRange, 40, BASE10) + numThreat_Rx_GaindBm + convertTodBm(numPlatform_RCS, 10, BASE10)  + convertTodBm(numRange_losses, 20, BASE10) )

def friis_dB(ERPt, range, waveform, losses):
    raise NotImplementedError