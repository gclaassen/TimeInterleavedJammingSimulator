import math

def convertERPdBm(power_W, gain):
 return convertPower_WtodBm(power_W) + convertGain_dBm(gain)

def convertPower_WtodBm(power_W):
  return 10*log10(power_W)

def convertGain_dBm(gain):
  return 10*math.log10(gain)

def skinReturnPower(Threat_Tx_ERP, Threat_Tx_Fc,  Threat_Rx_GaindBm, Platform_RCS, Range, Range_losses):
 return (Threat_Tx_ERP - 103 - 20*math.log(Threat_Tx_Fc) - 40*math.log(Range) + Threat_Rx_GaindBm + 10*math.log(Platform_RCS) + 20*log(Range_losses))
