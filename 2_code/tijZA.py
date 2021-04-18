import math
import common
import cartesian
import numpy as np

def calculateZoneAssessment(timeOfCoincidence_us, pltf_flightPath, threat_location):
    Rc = calculatePlatformDistance_m(timeOfCoincidence_us, pltf_flightPath, threat_location)
    Rm = calculateMaxRadarRange_m()
    Rb = calculateBurnthroughRange_m()
    Rn = calculateZoneAssessmentValue(Rc, Rm, Rb)

    return [Rc, Rm, Rb, Rn]

## get distance between platform and radar
def calculatePlatformDistance_m(timeOfCoincidence_us, pltf_flightPath, threat_location):
    
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
    
    ## get the distance between platform and threat
    return cartesian.displacement3dSpace (pltfPathArray, threat_location)

#TODO:
def calculateMaxRadarRange_m():
    return 0.0

#TODO:
def calculateBurnthroughRange_m():
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


