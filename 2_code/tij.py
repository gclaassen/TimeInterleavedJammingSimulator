class cTIJ:
    radar_id: int = 0

    # za
    za: float = 0
    platformDistance_km: float = 0.0
    maxRadarRange_km: float = 0.0
    burnthroughRange_km: float = 0.0
    minIJRadarRange_km: float = 0.0

    # ma
    ma: float = 0

    # JPP
    jpp: float = 0
    jpp_req: float = 0
    jpp_dif: float = 0

    cpi: float = 0
    cpi_startAt: int = 0

    SNR_dB: float = 0
    SNR_NJ_dB: float = 0
    SNR_INJ_dB: float = 0

    Pfa: float = 0
    Pd: float = 0
    Pd_min: float = 0
    Pd_min_achieved: float = 0
    Njamming: float = 0

    def __init__(self, numRadar_ID, numCPI, Pfa, Pd, Pd_min):
        self.radar_id = numRadar_ID
        self.cpi = numCPI
        self.Pfa = Pfa
        self.Pd = Pd
        self.Pd_min = Pd_min