import numpy as np

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

def sgn(x):
    if x<0:
        return -1
    if x==0:
        return 0
    if x>0:
        return 1

def profileCreatorInterval():
    pass