import math
import common
import cartesian
import numpy as np
import mathRadar as radarmath


def calculateplatformDistance_km(timeOfCoincidence_us, pltf_flightPath, threat_location):
    """Get the current distance between platform and radar

    Args:
        timeOfCoincidence_us ([float]): The time of the pulse coincidence
        pltf_flightPath ([cPlatform.flightPath]): The platform's cartesian flightpath
        threat_location ([cThreat.location]): The cartesian location of the threat

    Returns:
        [float]: The current distance Rc_km
    """

    pltfPathArray = cartesian.initializeCartesianArray(1)

    # determine new platform coordinates
    ## get the node to where the platform is flying towards
    if(timeOfCoincidence_us <= pltf_flightPath[-1][common.TOTAL_TIME]):
        nextNodeIdx = np.min(np.where(timeOfCoincidence_us < pltf_flightPath[:][common.TOTAL_TIME]))
    else:
        nextNodeIdx = (pltf_flightPath[-1][common.TOTAL_TIME].size - 1)

    ## get the node where the platform was previously
    prevNodeIdx = nextNodeIdx - 1

    ## get the distance displaced by platform at coincidence
    pltf_rDisp = cartesian.displacementInTime(timeOfCoincidence_us, pltf_flightPath[nextNodeIdx][common.PLF_SPEED])

    ## get the cartesian coordinates with the distance displaced and the angles
    [pltfPathArray[0][common.XCOORD], pltfPathArray[0][common.YCOORD], pltfPathArray[0][common.ZCOORD]] = cartesian.polarToCartesian(pltf_rDisp, pltf_flightPath[nextNodeIdx][common.ANGLE_AZI], pltf_flightPath[nextNodeIdx][common.ANGLE_ELEV])

    ## get the cartesian coordinates
    [pltfPathArray[0][common.XCOORD], pltfPathArray[0][common.YCOORD], pltfPathArray[0][common.ZCOORD]] = cartesian.updateCoord(pltf_flightPath[prevNodeIdx], pltfPathArray[0])

    ## get the distance between platform and threat in km
    return radarmath.convertRange_MeterToKiloMeter(cartesian.displacement3dSpace (pltfPathArray, threat_location))

def calculateZoneAssessmentValue(Rc_km, Rm_km, Rb_km):
    """Calculate the zone assessment value
    Rdelta = Rm - Rb
    ZA = (Rdelta - (Rc - Rb))/Rdelta

    Args:
        Rc_km ([float]): the current line of sight distance between platform and radar in kilometer
        Rm_km ([float]): The maximum detectable range wrt the required probability of detection of the platform in kilometer
        Rb_km ([float]): The burnthrough range when the jammer is always active on the threat radar in kilometer

    Returns:
        [float]: The zone assessment value between 0 (out of detection range) and 1 (inside burnthrough range)
    """
    Rdelta_km = Rm_km - Rb_km

    if(Rdelta_km > 0):
        if (Rc_km < Rb_km):
            ZA = 1
        elif (Rc_km > Rm_km):
            ZA = 0
        else:
            ZA = (Rdelta_km - (Rc_km - Rb_km) )/Rdelta_km
    elif(Rb_km > 0):
        ZA = 1
    else:
        ZA = 0
    return ZA