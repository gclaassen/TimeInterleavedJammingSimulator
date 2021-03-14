import math
import common

# RADAR EQUATION
def convertERPdBm(power_W, gain):
 return convertPowerWtodBm(power_W) + convertGaindBm(gain)

def convertPowerWtodBm(power_W):
  return 10*math.log10(power_W)

def convertGaindBm(gain):
  return 10*math.log10(gain)

def skinReturnPower(Threat_Tx_ERP, Threat_Tx_Fc,  Threat_Rx_GaindBm, Platform_RCS, Range, Range_losses):
 return (Threat_Tx_ERP - 103 - 20*math.log(Threat_Tx_Fc) - 40*math.log(Range) + Threat_Rx_GaindBm + 10*math.log(Platform_RCS) + 20*math.log(Range_losses))

def friis_dB(ERPt, range, waveform, losses):
    raise NotImplementedError

## LOSSES
def attenuation(wavelen, Rc):
    return ((common.STERADIANS*Rc)/wavelen) ^ 2


def attenuation_dB(wavelen_MHz, Rc_m):
    return -27.55 + 20*math.log10(Rc_m) + 20*math.log(wavelen_MHz)