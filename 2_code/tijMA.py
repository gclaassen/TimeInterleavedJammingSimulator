from dataclasses import dataclass
import common

# Sum should always equal to 1
@dataclass(frozen=True, order=True)
class cWeights:
    mode_weight: float = 0.34
    za_weight: float = 0.33
    lethalRange_weight: float = 0.33
    JammingPercentage_weight: float = 0.0

@dataclass(frozen=True, order=True)
class cModeWeigth:
    TS: float = 0.25
    TA: float = 0.5
    TT: float = 0.75
    MG: float = 1.0

def threatValueCalculation(mode, ZA, inLethalRange, JPdifference_norm):
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

    return (cWeights.mode_weight * modeVal) + (cWeights.za_weight * ZA) + (cWeights.lethalRange_weight * inLethalRange) + (cWeights.JammingPercentage_weight * JPdifference_norm)