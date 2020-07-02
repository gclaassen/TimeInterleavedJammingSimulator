import numpy as np
from numba import vectorize

def ranking(threatCategoriesList, p):
    sumVal = 0
    n = threatCategoriesList.__len__()

    for xk in threatCategoriesList:
        sumVal += sgn(xk)*np.abs(xk)**(1/p)
    return ((1/n)*sumVal)**p


def rankingWeigthed(threatCategoriesList, weights, p):
    sumVal = 0
    weigthVal = 0

    for idx, xk in enumerate(threatCategoriesList):
        weigthVal += weights[idx]
        sumVal += weights[idx]*sgn(xk)*np.abs(xk)**(1/p)

    return ((1/weigthVal)*sumVal)**p

def sumParam(threatParamList):
    return sum(threatParamList)

def normalizedParam(ThreatList, sumVal, index):
    for idx, threat in enumerate(ThreatList):
        ThreatList[idx,index] = threat[index]/sumVal
    return ThreatList[:,index]

def normalizeThreat(threatList, threatListShape):
    normalizedThreatList = np.empty_like(threatListShape, dtype=threatListShape.dtype)
    
    sumMa = sumParam(threatList[:,0])
    sumPj = sumParam(threatList[:,1])
    sumReqJamming = sumParam(threatList[:,2])
    
    normalizedThreatList[:,0] = normalizedParam(threatList,sumMa,0)
    normalizedThreatList[:,1] = normalizedParam(threatList,sumPj,1)
    normalizedThreatList[:,2] = normalizedParam(threatList,sumReqJamming,2)
    
    return normalizedThreatList

def sgn(x):
    if x<0:
        return -1
    if x==0:
        return 0
    if x>0:
        return 1

def profileCreatorInterval():
    # best to do it in parallel -> GPU programming
    # how do we do this with the amount of info available
    pass