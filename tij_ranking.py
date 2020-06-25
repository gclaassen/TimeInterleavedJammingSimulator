import numpy as np

def ranking(categoriesList, p):
    sumVal = 0
    n = categoriesList.__len__()
    for xk in categoriesList:
        sumVal += sgn(xk)*np.abs(xk)**(1/p)
    return ((1/n)*sumVal)**p


def rankingWeigthed(weigthedCategoriesList, p):
    weight = 0
    x = 1
    sumVal = 0
    weigthVal = 0

    for xk in weigthedCategoriesList:
        weigthVal += xk[weight]
        sumVal += xk[weight]*sgn(xk[x])*np.abs(xk[x])**(1/p)

    return ((1/weigthVal)*sumVal)**p

def sgn(x):
    if x<0:
        return -1
    if x==0:
        return 0
    if x>1:
        return 1

def profileCreatorInterval():
    pass