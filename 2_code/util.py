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
    idx = np.max(np.where(array<=value))
    return idx