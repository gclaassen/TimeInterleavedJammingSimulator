import math
import common


def convertPowerWattTodBm(power_W):
    return 10*math.log10(power_W) + 30


def convertPowerdBmToWatt(power_dBm):
    x = math.pow(power_dBm/10, 10)
    return (1*x)/1000

def convertTimeSecondsToNanoseconds(time_s):
    return time_s*1e9

def convertTimeMinutesToSeconds(time_m):
    return time_m*60


def convertRadarTypeStringToInt(sRadarType):
    if sRadarType == common.sSEARCH:
        return common.SEARCH
    elif sRadarType == common.sACQUISITION:
        return common.ACQUISITION
    elif sRadarType == common.sTRACKING:
        return common.TRACKING
    elif sRadarType == common.sMISSILE_GUIDANCE:
        return common.MISSILE_GUIDANCE
    else:
        return None


def convertToErp(power, gain):
    return power*gain
