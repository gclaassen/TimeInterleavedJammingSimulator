import math

RET_ERROR = 0x0F0C
RET_WARNING = 0x0BAD

THREATDIR   = '../Time-Interleaved-Jamming-Simulator/threats.json'
PLATFORMDIR = '../Time-Interleaved-Jamming-Simulator/platform.json'
JAMMERDIR   = '../Time-Interleaved-Jamming-Simulator/jammer.json'

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

# Platform JSON key values
PLF_PLATFORM                = 'platform'
PLF_RCS                     = 'rcs'
PLF_FLIGHTPATH              = 'flightpath'
PLF_FLIGHTPATH_SIZE         = 4 #x, y, z, speed
PLF_XCOORD                  = "X_coord"
PLF_YCOORD                  = "Y_coord"
PLF_ZCOORD                  = "Z_coord"
PLF_SPEED                   = "velocity_ms"

# Threat JSON key values
THREAT_THREATS              = 'threats'
THREAT_ID                   = 'radar_id'

THREAT_EMITTERS             = 'emitters'
THREAT_MODES                = 'modes'
THREAT_EMITTERMODES_SIZE    = 11
THREAT_EMITTER_ID           = 'emitter_id'
THREAT_MODEID               = 'mode_id'
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
THREAT_LOCATION_SIZE        = 3
THREAT_XCOORD               = "X_coord"
THREAT_YCOORD               = "Y_coord"
THREAT_ZCOORD               = "Z_coord"

JAMMER_CHANNEL              = "channels"
JAMMER_CHANNEL_RANGE        = "channel_range"
JAMMER_CHANNEL_START        = "channel_start_MHz"
JAMMER_CHANNEL_STOP         = "channel_stop_MHz"
JAMMER_TIME_INTERVAL        = "interval_time_s"
JAMMER_CHANNEL_RANGE_SIZE   = 2 #start, stop