from dataclasses import dataclass

# Sum should always equal to 1
@dataclass(frozen=True, order=True)
class cWeights:
    mode_weight: float = 0.25
    za_weight: float = 0.25
    lethalRange_weight: float = 0.25
    JammingPercentage_weight: float = 0.25

@dataclass(frozen=True, order=True)
class cModeWeigth:
    TS: float = 0.25
    TA: float = 0.5
    TT: float = 0.75
    MG: float = 1.0

def threatValueCalculation(weights, mode, ZA, inLethalRange, JPdifference_norm):
    return (weights.mode_weight * mode) + (weights.za_weight * ZA) + (weights.lethalRange_weight * inLethalRange) + (weights.JammingPercentage_weight * JPdifference_norm)