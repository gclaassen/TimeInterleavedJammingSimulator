import numpy as np
import common
import jsonParser

class Channel:
    oecm_time_ms: int=0
    esm_time_ms: int=0
    interval_time_ms: int = 0
    channel_range_MHz = None

    pulse_profile = None
    jammer_profile = None
    interval_Tstart: int = 0
    interval_Tstop: int = 0
    
    def __init__(self, channelList, channelRange):
        self.oecm_time_ms = channelList[common.JAMMER_JAMMING_TIME]
        self.esm_time_ms = channelList[common.JAMMER_LOOKTHROUGH_TIME]
        self.interval_time_ms = self.oecm_time_ms + self.esm_time_ms
        self.channel_range_MHz = channelRange


class Jammer:
    cChannel: None
    channel_size: int = 0
    channel_ranges_MHz = None

    def __init__(self, jammerList):
        self.channel_ranges_MHz = convertJammerChannelsJsonToArray(
            jammerList[common.JAMMER_CHANNEL])
        self.channel_size = jammerList[common.JAMMER_CHANNEL].__len__()
        
        self.cChannel = [None]*self.channel_size
        for idx, channelList in enumerate(jammerList[common.JAMMER_CHANNEL]):
            self.cChannel[idx] = Channel(channelList, self.channel_ranges_MHz[idx])


def convertJammerChannelsJsonToArray(jsonJammerChansDict):
    jcArr = np.empty(shape=(jsonJammerChansDict.__len__()), dtype=[(common.JAMMER_CHANNEL_START,int),(common.JAMMER_CHANNEL_STOP,int)], order='C')
    for idx, jc in enumerate(jsonJammerChansDict):
        jcArr[idx][common.JAMMER_CHANNEL_START] = jc[common.JAMMER_CHANNEL_START]
        jcArr[idx][common.JAMMER_CHANNEL_STOP] = jc[common.JAMMER_CHANNEL_STOP]
    return jcArr

def profileCreatorJammingThreat():
    pass

