import math

RET_ERROR = 0x0F0C
RET_WARNING = 0x0BAD

THREATDIR   = '1_datastore/0_manual/threats.json'
PLATFORMDIR = '1_datastore/0_manual/platform.json'
JAMMERDIR   = '1_datastore/0_manual/jammer.json'

# Global Values
STERADIANS = 4*math.pi

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

XCOORD                  = "X_coord"
YCOORD                  = "Y_coord"
ZCOORD                  = "Z_coord"

TIME                    = "time"
DISTANCE                = "distance"

# Platform JSON key values
PLF_PLATFORM                = 'platform'
PLF_RCS                     = 'rcs'
PLF_FLIGHTPATH              = 'flightpath'
PLF_FLIGHTPATH_SIZE         = 4 #x, y, z, speed
PLF_SPEED                   = "velocity_ms"

# Threat JSON key values
THREAT_THREATS              = 'threats'
THREAT_ID                   = 'radar_id'
THREAT_NAME                 = 'radar_name'
THREAT_EMITTERS             = 'emitters'
THREAT_MODES                = 'modes'
THREAT_EMITTERMODES_SIZE    = 11
THREAT_EMITTER_ID           = 'emitter_id'
THREAT_MODE_ID               = 'mode_id'
THREAT_TYPE                 = 'type'
THREAT_ERP                  = "erp"
THREAT_PEAKPOWER            = 'power_peak_W'
THREAT_GAIN                 = 'gain'
THREAT_FREQ                 = 'frequency_MHz'
THREAT_PRI                  = 'pri_us'
THREAT_PW                   = 'pulse_width_us'
THREAT_RANGE                = 'range_max_m'
THREAT_ALT                  = 'altitude_max_m'
THREAT_ISERP                = 'isERP'
THREAT_LOCATION             = 'location'
THREAT_CPI                  = 'cpi'
THREAT_PERCENTAGEJAMMING    = 'percentage_jamming'
THREAT_LOCATION_SIZE        = 3

JAMMER_CHANNEL              = "channels"
JAMMER_CHANNEL_START        = "channel_start_MHz"
JAMMER_CHANNEL_STOP         = "channel_stop_MHz"
JAMMER_JAMMING_TIME         = "oecm_time_ms"
JAMMER_LOOKTHROUGH_TIME     = "esm_time_ms"
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

PulseArrSize = 3

INTERVAL_LIB_RADAR_ID                   = 0
INTERVAL_LIB_PULSE_START                = 1
INTERVAL_LIB_PULSE_STOP                 = 2
INTERVAL_LIB_PRI_US                     = 3
INTERVAL_LIB_PW_US                      = 4
INTERVAL_LIB_PULSE_NUMBER               = 5
INTERVAL_LIB_COINCIDENCE_NUMBER         = 6
INTERVAL_INTERVAL_COINCIDENCE_PERC      = 7
INTERVAL_LIB_OECM_TIME_US               = 8
INTERVAL_LIB_SIZE                       = 9