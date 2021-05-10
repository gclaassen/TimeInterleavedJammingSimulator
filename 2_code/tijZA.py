import math
import common
import cartesian
import numpy as np
import mathRadar as radmath

def calculateZoneAssessment(timeOfCoincidence_us, pltf_flightPath, threat_location):
    Rc = calculateplatformDistance_km(timeOfCoincidence_us, pltf_flightPath, threat_location)
    Rm = calculatemaxRadarRange_km()
    Rb = calculateburnthroughRange_km()
    Rn = calculateZoneAssessmentValue(Rc, Rm, Rb)

    return [Rc, Rm, Rb, Rn]

# def calculateZoneAssessment(Rc, Rm, Rb):
#     return calculateZoneAssessmentValue(Rc, Rm, Rb)

## get distance between platform and radar
def calculateplatformDistance_km(timeOfCoincidence_us, pltf_flightPath, threat_location):
    pltfPathArray = cartesian.initializeCartesianArray(1)

    # determine new platform coordinates
    ## get the node to where the platform is flying towards
    nextNodeIdx = np.min(np.where(timeOfCoincidence_us < pltf_flightPath[:][common.TOTAL_TIME]))
    ## get the node where the platform was previously
    prevNodeIdx = nextNodeIdx - 1

    ## get the distance displaced by platform at coincidence
    pltf_rDisp = cartesian.displacementInTime(timeOfCoincidence_us, pltf_flightPath[nextNodeIdx][common.PLF_SPEED])

    ## get the cartesian coordinates with the distance displaced and the angles
    [pltfPathArray[0][common.XCOORD], pltfPathArray[0][common.YCOORD], pltfPathArray[0][common.ZCOORD]] = cartesian.polarToCartesian(pltf_rDisp, pltf_flightPath[nextNodeIdx][common.ANGLE_AZI], pltf_flightPath[nextNodeIdx][common.ANGLE_ELEV])

    ## get the cartesian coordinates
    [pltfPathArray[0][common.XCOORD], pltfPathArray[0][common.YCOORD], pltfPathArray[0][common.ZCOORD]] = cartesian.updateCoord(pltf_flightPath[prevNodeIdx], pltfPathArray[0])

    ## get the distance between platform and threat in km
    return radmath.convertRange_MeterToKiloMeter(cartesian.displacement3dSpace (pltfPathArray, threat_location))

#TODO:
def calculatemaxRadarRange_km():
    return 0.0

#TODO:
def calculateburnthroughRange_km():
    return 0.0

def calculateZoneAssessmentValue(Rc, Rm, Rb):
    Rdelta = Rm - Rb

    if(Rdelta > 0):
        if (Rc < Rb):
            Rn = 1
        elif (Rc > Rm):
            Rn = 0
        else:
            Rn = (Rdelta - (Rc - Rb) )/Rdelta
    elif(Rb > 0):
        Rn = 1
    else:
        Rn = 0
    return Rn


