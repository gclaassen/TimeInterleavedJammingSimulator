import math

RET_ERROR = 0xF0C
RET_WARNING = 0xBAD

THREATDIR   = '../Time-Interleaved-Jamming/threats.json'
PLATFORMDIR = '../Time-Interleaved-Jamming/platform.json'

# Global Values
STERADIANS = 4*math.pi

# Radar Types
SEARCH              = 0
ACQUISITION         = 1
TRACKING            = 2
FIRE_CONTROL        = 3
MISSILE_GUIDANCE    = 4

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
THREAT_EMITTER_ID           = 'emitter_id'

THREAT_MODES                = 'modes'
THREAT_MODES_SIZE           = 10
THREAT_ERP                  = "erp"
THREAT_FREQ                 = 'frequency_MHz'
THREAT_GAIN                 = 'gain'
THREAT_ISERP                = 'isERP'
THREAT_MODEID               = 'mode_id'
THREAT_PEAKPOWER            = 'power_peak_W'
THREAT_PRF                  = 'prf_Hz'
THREAT_PW                   = 'pulse_width_us'
THREAT_RANGE                = 'range_max_m'
THREAT_TYPE                 = 'type'

THREAT_LOCATION             = 'location'
THREAT_LOCATION_SIZE        = 3
THREAT_XCOORD               = "X_coord"
THREAT_YCOORD               = "Y_coord"
THREAT_ZCOORD               = "Z_coord"

