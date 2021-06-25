def initSeparateListOfObjects(size):
    list_of_objects = list()
    for _ in range(0,size):
        list_of_objects.append( list() ) #different object reference each time
    return list_of_objects