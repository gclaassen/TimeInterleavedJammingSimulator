import threats
import plf
import common
import jsonParser
import visualize

def main():
    # Initialize
    # init platform class instance
    pf = plf.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    th = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))
    
    # visualize the world
    visualize.worldview(pf, th)
    


    pass


if __name__ == "__main__":
    main()
