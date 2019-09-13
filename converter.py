import math
import common


def convertPowerWattTodBm(power_W):
    return 10*math.log10(power_W) + 30


def convertPowerdBmToWatt(power_dBm):
    x = math.pow(power_dBm/10, 10)
    return (1*x)/1000


def convertRadarTypeStringToInt(sRadarType):
    if sRadarType == 'SEARCH':
        return common.SEARCH
    elif sRadarType == 'ACQ':
        return common.ACQUISITION
    elif sRadarType == 'TRACK':
        return common.TRACKING
    elif sRadarType == 'FIRECONTROL':
        return common.FIRE_CONTROL
    elif sRadarType == 'MISSILEGUIDE':
        return common.MISSILE_GUIDANCE
    else:
        return None


def convertToErp(power, gain):
    return power*gain
