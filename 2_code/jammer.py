import numpy as np
import common
import jsonParser
import mathRadar as radmath

class cChannel:
    oInterval: None
    oThreatLib: None
    oCoincidences: None
    oecm_time_us: int=0
    esm_time_us: int=0
    interval_time_us: int = 0
    channel_range_MHz = None

    def __init__(self, channelList, channelRange):
        self.oecm_time_us = radmath.convertTime_MilisecondsToMicroseconds(channelList[common.JAMMER_JAMMING_TIME])
        self.esm_time_us = radmath.convertTime_MilisecondsToMicroseconds(channelList[common.JAMMER_LOOKTHROUGH_TIME])
        self.interval_time_us = self.oecm_time_us + self.esm_time_us
        self.channel_range_MHz = channelRange


class cJammer:
    oChannel = []
    channel_size: int = 0
    channel_ranges_MHz = None
    jammer_bin_size: float = 0
    jammer_power_kW: float = 0
    jammer_bandwidth_MHz: float = 0
    jammer_gain_dB: float = 0

    def __init__(self, jammerList):
        self.channel_ranges_MHz = convertJammerChannelsJsonToArray(
            jammerList[common.JAMMER_CHANNEL])
        self.channel_size = jammerList[common.JAMMER_CHANNEL].__len__()
        self.jammer_bin_size = jammerList[common.JAMMER_ENVELOPE_BIN_SIZE]
        self.jammer_bandwidth_MHz = jammerList[common.JAMMER_BANDWIDTH_MHZ]
        self.jammer_gain_dB = jammerList[common.JAMMER_GAIN_DB]
        self.jammer_power_kW = jammerList[common.JAMMER_POWER_KW]

        self.oChannel = [None]*self.channel_size
        for idx, channelList in enumerate(jammerList[common.JAMMER_CHANNEL]):
            self.oChannel[idx] = cChannel(channelList, self.channel_ranges_MHz[idx])


def convertJammerChannelsJsonToArray(jsonJammerChansDict):
    jcArr = np.empty(shape=(jsonJammerChansDict.__len__()), dtype=[(common.JAMMER_CHANNEL_START,int),(common.JAMMER_CHANNEL_STOP,int)], order='C')
    for idx, jc in enumerate(jsonJammerChansDict):
        jcArr[idx][common.JAMMER_CHANNEL_START] = jc[common.JAMMER_CHANNEL_START]
        jcArr[idx][common.JAMMER_CHANNEL_STOP] = jc[common.JAMMER_CHANNEL_STOP]
    return jcArr

def profileCreatorJammingThreat():
    pass