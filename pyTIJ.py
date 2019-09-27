import os, getopt, sys
import threats
import plf
import common
import jsonParser
import visualize

def argumentExtraction(argv):
    setViz = False

    try:
        [opts, argv] = getopt.getopt(
            argv, "h:v", ["help", "visualize"])
    except getopt.GetoptError:
        helpPrints()
        return None
    for opt, arg in opts:
        if opt == '-h':
            helpPrints()
            exit()
        elif opt in ("-v", "--visualize"):
            setViz = True
            print('Visualization set to True')

    return [setViz]


def helpPrints():
    print('\npyTIJ.py <arguments> \n')
    print('~~~ARGUMENT LIST~~~\n')
    print('-v:\tvisualize\n')


def main(argv):
    doViz = False
    
    doViz = argumentExtraction(argv)
    
    # Initialize
    # init platform class instance
    pf = plf.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    th = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))
    
    # visualize the world
    if(doViz == True):
        visualize.worldview(pf, th)


    pass


if __name__ == "__main__":
    main(sys.argv[1:])
