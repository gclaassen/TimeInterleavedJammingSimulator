import common
import math


def attenuation(wavelen, Rc):
    return ((common.STERADIANS*Rc)/wavelen) ^ 2


def attenuation_dB(wavelen_MHz, Rc_m):
    return -27.55 + 20*math.log10(Rc_m) + 20*math.log(wavelen_MHz)