import threats
import plf
import common
import jsonParser


def main():
    # Initialize
    # init platform class instance
    pf = plf.Platform(jsonParser.parseJsonFile(common.PLATFORMDIR))
    # init threats (mulitple instances of threat class)
    th = threats.convertThreatJsonToClass(
        jsonParser.parseJsonFile(common.THREATDIR))

    pass


if __name__ == "__main__":
    main()
