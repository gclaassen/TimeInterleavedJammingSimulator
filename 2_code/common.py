import math
from os import access

# CONSTANTS: RADAR
STERADIANS = 4*math.pi
c = 299792458 #Speed of Light (m/s)
RadarEquationConstant = 239.3 # Range in km
T0 = 290 # [K]
Boltzman_k = 1.38*math.pow(10,-23) # W/Hz
kT0 = Boltzman_k*290 # W/Hz
kT0_dB = -204 # dBW/Hz

Lp_1D_dB = 1.6
Lp_2D_dB = 3.2
La_dB = 0.01

Fr_dB= 1
Ft_dB = 1

# CONSTANS: JAMMER
Qj = 0.3 #0.3 - 0.6 worst to best jamming quality factor

Lja_dB = 0.01

Fjt_dB = 1
Fjp_dB = -3 # circular antenna

MA_MODE_WEIGHT = 0.25
MA_ZA_WEIGHT = 0.25
MA_LETHALRANGE_WEIGHT = 0.25
MA_INTERMITTENTJAMMING_WEIGHT = 0.25

ARG_JAMMINGBINPRI = False
ARG_CUTPULSEATEND = False
ARG_JAMMINGWINDOWEXPERIMENTAL = False
IGNOREBURNTHROUGH = False


THREATDIR   = '1_datastore/0_manual/'
PLATFORMDIR = '1_datastore/0_manual/'
JAMMERDIR   = '1_datastore/0_manual/'

THREATFILE = 'threats.json'
PLATFORMFILE = 'platform.json'
JAMMERFILE = 'jammer.json'

RESULTDIR = '4_output/data/'

RESULTMODESLOG = 'modesChangeLog'
RESULTRANGELOG = 'rangeLog'
RESULTLETHALRANGELOG = 'lethalrangeLog'
RESULTCOINCIDENCEPERCENTAGELOG = 'coincidenePercLog'
RESULTJAMMINGLOG = 'resultJammingLog'
DETECTIONSLOG = 'decetionsLog'
CPILOG = 'cpiLog'

RESULTFILEEXT = '.npy'

TEST_TIJ = 0
TEST_HIGHESTMODE = 1

#string Radar Modes
sSEARCH              = 'TS'
sACQUISITION         = 'TA'
sTRACKING            = 'TT'
sMISSILE_GUIDANCE    = 'MG'

#numeric Radar Modes
SEARCH              = 0 # TS
ACQUISITION         = 1 # TA
TRACKING            = 2 # TT
MISSILE_GUIDANCE    = 3 # MG

dictModes = {SEARCH: sSEARCH, ACQUISITION: sACQUISITION, TRACKING: sTRACKING, MISSILE_GUIDANCE: sMISSILE_GUIDANCE}

XCOORD                  = "X_coord"
YCOORD                  = "Y_coord"
ZCOORD                  = "Z_coord"

TIME                    = "time_us"
TOTAL_TIME              = "totalTime_us"
DISTANCE                = "distance_m"

ANGLE_AZI               = "azi_angle"
ANGLE_ELEV              = "elev_angle"

# Platform JSON key values
PLF_PLATFORM                = 'platform'
PLF_RCS                     = 'rcs'
PLF_FLIGHTPATH              = 'flightpath'
PLF_FLIGHTPATH_SIZE         = 4 #x, y, z, speed
PLF_SPEED                   = "velocity_ms"

# Threat JSON key values
THREAT_THREATS                      = 'threats'
THREAT_ID                           = 'radar_id'
THREAT_NAME                         = 'radar_name'
THREAT_EMITTERS                     = 'emitters'
THREAT_MODES                        = 'modes'
THREAT_EMITTERMODES_SIZE            = 11
THREAT_EMITTER_ID                   = 'emitter_id'
THREAT_EMITTER_NOISEFIGURE_DB       = 'noise_figure_dB'
THREAT_START_MODE                   = 'start_mode'
THREAT_MODE_ID                      = 'mode_id'
THREAT_MODE_TYPE                    = 'type'
THREAT_AVGPOWER_KW                  = 'power_avg_kW'
THREAT_PEAKPOWER_KW                 = 'power_peak_kW'
THREAT_GAIN                         = 'gain'
THREAT_FREQ_MHZ                     = 'frequency_MHz'
THREAT_PRI_US                       = 'pri_us'
THREAT_PW_US                        = 'pulse_width_us'
THREAT_DUTY_CYCLE                   = 'duty_cycle'
THREAT_RANGE_KM                     = 'range_max_km'
THREAT_LETHAL_RANGE_KM              = 'ws_range_km'
THREAT_ALT_KM                       = 'altitude_max_km'
THREAT_LOCATION                     = 'location'
THREAT_CPI                          = 'cpi'
THREAT_CPI_REAL                     = 'cpi_real'
THREAT_CPI_AT_INTERVAL              = 'cpi_before_interval'
THREAT_PROB_DETECTION               = 'Pd'
THREAT_PROB_DETECTION_REAL          = 'Pd_real'
THREAT_PROB_DETECTION_MIN           = 'Pd_min'
THREAT_PROB_DETECTION_CUMULATIVE    = 'Pd_cumulative'
THREAT_PROB_FALSE_ALARM             = 'Pfa'
THREAT_PROB_FALSE_ALARM_REAL        = 'Pfa_real'
THREAT_LOCATION_SIZE                = 3

JAMMER_CHANNEL              = "channels"
JAMMER_CHANNEL_START        = "channel_start_MHz"
JAMMER_CHANNEL_STOP         = "channel_stop_MHz"
JAMMER_POWER_KW             = "power_peak_kw"
JAMMER_GAIN_DB              = "gain_dB"
JAMMER_BANDWIDTH_MHZ        = "bandwidth_MHz"
JAMMER_JAMMING_TIME         = "oecm_time_ms"
JAMMER_LOOKTHROUGH_TIME     = "esm_time_ms"
JAMMER_ENVELOPE_BIN_SIZE_PRI    = "jamming_envelope_bin_size_PRI"
JAMMER_ENVELOPE_BIN_SIZE_PW     = "jamming_envelope_bin_size_PW"
JAMMER_CHANNEL_RANGE_SIZE   = 2 #start, stop

def convertRadarTypeStringToInt(strRadarType):
    if strRadarType == sSEARCH:
        return SEARCH
    elif strRadarType == sACQUISITION:
        return ACQUISITION
    elif strRadarType == sTRACKING:
        return TRACKING
    elif strRadarType == sMISSILE_GUIDANCE:
        return MISSILE_GUIDANCE
    else:
        return None

INTERVAL_LIB_RADAR_ID                   = 0
INTERVAL_LIB_PULSE_START                = 1
INTERVAL_LIB_PULSE_STOP                 = 2
INTERVAL_LIB_NOISE_PULSE_START          = 3
INTERVAL_LIB_NOISE_PULSE_STOP           = 4
INTERVAL_LIB_PRI_US                     = 5
INTERVAL_LIB_PW_US                      = 6
INTERVAL_LIB_PULSE_NUMBER               = 7
INTERVAL_LIB_COINCIDENCE_NUMBER         = 8
INTERVAL_INTERVAL_COINCIDENCE_PERC      = 9
INTERVAL_STOP_TIME_US                   = 10
INTERVAL_JAMMING_BIN_START_ENVELOPE     = 11
INTERVAL_JAMMING_BIN_STOP_ENVELOPE      = 12
INTERVAL_LIB_SIZE                       = 13