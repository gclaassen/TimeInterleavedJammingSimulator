import math
import common


def convertPowerWattTodBm(power_W):
    return 10*math.log10(power_W) + 30


def convertPowerdBmToWatt(power_dBm):
    x = math.pow(power_dBm/10, 10)
    return (1*x)/1000


def convertRadarTypeStringToInt(sRadarType):
    if sRadarType == 'SS':
        return common.SEARCH
    elif sRadarType == 'TA':
        return common.ACQUISITION
    elif sRadarType == 'TT':
        return common.TRACKING
    elif sRadarType == 'TI':
        return common.TARGET_ILLUMINATE
    elif sRadarType == 'MG':
        return common.MISSILE_GUIDANCE
    else:
        return None


def convertToErp(power, gain):
    return power*gain
