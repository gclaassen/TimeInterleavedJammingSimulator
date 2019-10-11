import math

def setERPdBm(power_W, gain):
 return convertPower_WtodBm(power_W) + convertGain_dBm(gain)

def convertPower_WtodBm(power_W):
  return 10*log10(power_W)

def convertGain_dBm(gain):
  return 10*math.log10(gain)
