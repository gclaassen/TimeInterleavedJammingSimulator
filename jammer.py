import numpy as np
import common
import jsonParser


class Jammer:
    interval_time: int=0
    channels: int=0
    channel_ranges = None
    current_profiles = None
    jammer_profile = None

    def __init__(self, jammerList):
        self.interval_time = jammerList[common.JAMMER_TIME_INTERVAL]
        self.channels = jammerList[common.JAMMER_CHANNEL]
        self.channel_ranges = convertJammerChannelsJsonToArray(
            jammerList[common.JAMMER_CHANNEL_RANGE])


def convertJammerChannelsJsonToArray(jsonJammerChansDict):
    jcArr = np.empty(shape=(jsonJammerChansDict.__len__()), dtype=[(common.JAMMER_CHANNEL_START,int),(common.JAMMER_CHANNEL_STOP,int)], order='C')
    for idx, jc in enumerate(jsonJammerChansDict):
        jcArr[idx][common.JAMMER_CHANNEL_START] = jc[common.JAMMER_CHANNEL_START]
        jcArr[idx][common.JAMMER_CHANNEL_STOP] = jc[common.JAMMER_CHANNEL_STOP]
    return jcArr

