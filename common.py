import math

RET_ERROR = 0xF0C
RET_WARNING = 0xBAD

THREATDIR   = '../Time-Interleaved-Jamming-Simulator/threats.json'
PLATFORMDIR = '../Time-Interleaved-Jamming-Simulator/platform.json'

# Global Values
STERADIANS = 4*math.pi

# Radar Types
SEARCH              = 0 # S
ACQUISITION         = 1 # TA
TRACKING            = 2 # TT
TARGET_ILLUMINATE   = 3 # TI
MISSILE_GUIDANCE    = 4 # MG

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
THREAT_THREATS             = 'threats'
THREAT_ID                   = 'radar_id'

THREAT_EMITTERS             = 'emitters'
THREAT_MODES                = 'modes'
THREAT_EMITTERMODES_SIZE    = 10
THREAT_EMITTER_ID           = 'emitter_id'
THREAT_MODEID               = 'mode_id'
THREAT_TYPE                 = 'type'
THREAT_ERP                  = "erp"
THREAT_PEAKPOWER            = 'power_peak_W'
THREAT_GAIN                 = 'gain'
THREAT_FREQ                 = 'frequency_MHz'
THREAT_PRF                  = 'prf_Hz'
THREAT_PW                   = 'pulse_width_us'
THREAT_RANGE                = 'range_max_m'
THREAT_ISERP                = 'isERP'

THREAT_LOCATION             = 'location'
THREAT_LOCATION_SIZE        = 3
THREAT_XCOORD               = "X_coord"
THREAT_YCOORD               = "Y_coord"
THREAT_ZCOORD               = "Z_coord"

