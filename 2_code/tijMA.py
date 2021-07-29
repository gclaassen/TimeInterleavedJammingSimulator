from dataclasses import dataclass
import common

# Sum should always equal to 1
@dataclass(frozen=True, order=True)
class cWeights:
    mode_weight: float = 0.1
    za_weight: float = 0.1
    lethalRange_weight: float = 0.1
    JammingPercentage_weight: float = 0.7

@dataclass(frozen=True, order=True)
class cModeWeigth:
    TS: float = 0.25
    TA: float = 0.5
    TT: float = 0.75
    MG: float = 1.0

def threatValueCalculation(mode, ZA, inLethalRange, JCP):
    modeVal = 0
    if mode == common.SEARCH:
        modeVal = cModeWeigth.TS
    elif mode == common.ACQUISITION:
        modeVal = cModeWeigth.TA
    elif mode == common.TRACKING:
        modeVal = cModeWeigth.TT
    elif mode == common.MISSILE_GUIDANCE:
        modeVal = cModeWeigth.MG
    else:
        None

    if JCP == 1:
        JCP = 0

    return (common.MA_MODE_WEIGHT * modeVal) + (common.MA_ZA_WEIGHT * ZA) + (common.MA_LETHALRANGE_WEIGHT * inLethalRange) + (common.MA_INTERMITTENTJAMMING_WEIGHT * JCP)