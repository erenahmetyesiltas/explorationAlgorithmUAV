from ExplorationAlg import Exploration

def main():

    # initialPoint list is the list which contains starting point's longitude,latitude and altitude
    initialPoint = [-35.36336068, 149.16535836, 15.0]

    # givenPoints list includes 2 points' longitude and latitude
    givenPoints = [
        [-35.36317379, 149.16535376],
        [-35.36308480, 149.16513282]
    ]

    # location is significant for lon-lat to x-y conversion and vice versa
    location = "Australia"

    gozlem = Exploration(initialPoint, givenPoints, location, initialPoint[2])

    # to get waypoints as longitude and latitude 
    # please use the list called "wayPointsListAsLatLong" in Exploration class
    for i in range(len(gozlem.wayPointsListAsLatLong)):
        print(i,"lat is ",gozlem.wayPointsListAsLatLong[i][0])
        print(i,"lon is ",gozlem.wayPointsListAsLatLong[i][1])

main()