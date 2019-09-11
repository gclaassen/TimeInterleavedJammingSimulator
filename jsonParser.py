import json

def parseJsonFile(jsonFile):
    jData = None
    with open(jsonFile) as jFileData:
        jData = json.load(jFileData)

    return jData

