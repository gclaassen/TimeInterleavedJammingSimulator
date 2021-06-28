import numpy as np

def initSeparateListOfObjects(size):
    list_of_objects = list()
    for _ in range(0,size):
        list_of_objects.append( list() ) #different object reference each time
    return list_of_objects

def find_nearestIndex(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx


def find_nearestIndexFloor(array, value):
    minArrayIdxs = np.where(array<=value)
    if minArrayIdxs[0].size != 0:
        idx = np.max(minArrayIdxs[0])
    else:
        idx = None
    return idx