import math
from sensor_msgs import *
from geographic_msgs import *
from pyproj import CRS, Transformer

class Exploration():

    # Position.Target to Waypoint convertion
    latLongCoordinatesOf4 = [[0]* 2 for _ in range(4)]
    referencePoint = [[0] for _ in range(2)]
    
    # to arrange the circular motion in the case which is min uav turning radius is bigger than camera vision distance
    comfortableFlightDist = 1

    # Yükseklik Belirlemek İÇin
    height = None

    ### Real variables 
    # r (= 2)
    selectedRadiusOfCamera = 2
    # max distance the camera can get net motion (= 1)
    maxDistanceForCamera = selectedRadiusOfCamera * math.sin(math.pi/6)
    #x' degree which be able to change (Real = 38). For testing it is 3
    degreeChangeable = 30
    necessaryDegree = degreeChangeable + 30
    necessaryDegreeRadian = necessaryDegree * math.pi / 180
    #x
    necessaryDistToStartObserv = selectedRadiusOfCamera * math.sin(necessaryDegreeRadian)
    # It is necessary to rotate the UAV correctly 
    rotationAlignmentDistance = 3


    # Selected Area's Points
    selectedPointId = None
    startingPoint = [[0.0],[0.0]]
    alignmentPoint = [[0.0],[0.0]]

    # Directions
    isVertical = False
    isHorizontal = False
    isUp = False
    isDown = False
    isRight = False
    isLeft = False

    # Initial Position
    x_coordinate = None
    y_coordinate = None
    z_coordinate = None

    # Route String
    route = None

    # Number of wayPoint Column
    totalWayPointNumber = 0

    # WayPoints array
    wayPoints = None
    wayPointsListAsLatLong = None

    # SelectedPoints array
    selectedPoints = [[0] * 2 for _ in range(4)]


    def __init__(self,initialPoint,givenPoints,location,specifiedHeight):

        self.height = specifiedHeight

        selectedPoints = [[0] * 2 for _ in range(4)]

        self.givenPointsTo4PointsCoordinates(givenPoints,selectedPoints)    
        
        # Starting point
        self.x_coordinate = initialPoint[0]
        self.y_coordinate = initialPoint[1]
        self.z_coordinate = initialPoint[2]

        # Get the 4 specified points in the class
        for i in range(len(self.latLongCoordinatesOf4)):
            for j in range(len(self.latLongCoordinatesOf4[0])):
                self.latLongCoordinatesOf4[i][j] = selectedPoints[i][j]

        # Set the starting point's longtide and latitude
        self.referencePoint[0] = initialPoint[0]
        self.referencePoint[1] = initialPoint[1]

        # Convertion of lan and lon to x and y according to its Location
        self.convertXY_To_RealLocations(location)

        # Redesign to coordinates to make the calculations better
        self.redesignTheCoordinates()

        # Executions
        self.setTheClosestPoint()
        self.setTheLongSideOfArea()

        initialPointXY = [initialPoint[0],initialPoint[1]]
        self.wayPoints.insert(0,initialPointXY)

        self.redesignTheAlignmentFrstPnt()

        self.wayPointsConvertionFromXYToLatLong(location)

        self.coordinates = self.wayPointsListAsLatLong

    def givenPointsTo4PointsCoordinates(self,givenPoints,sel4PointsCords):

        sel4PointsCords[0][0] = givenPoints[0][0]
        sel4PointsCords[0][1] = givenPoints[1][1]

        sel4PointsCords[1][0] = givenPoints[0][0]
        sel4PointsCords[1][1] = givenPoints[0][1]

        sel4PointsCords[2][0] = givenPoints[1][0]
        sel4PointsCords[2][1] = givenPoints[0][1]

        sel4PointsCords[3][0] = givenPoints[1][0]
        sel4PointsCords[3][1] = givenPoints[1][1]
        

    def setTheClosestPoint(self):
        distances = [0.0,0.0,0.0,0.0]

        for i in range(4):
            distances[i] = math.sqrt(math.pow(self.x_coordinate - self.selectedPoints[i][0],2) + math.pow(self.y_coordinate - self.selectedPoints[i][1],2))

        selectedPointId = 0
        minDist = distances[0]

        for i in range(4):
            if distances[i] < minDist:
                minDist = distances[i]
                selectedPointId = i

        self.selectedPointId = selectedPointId

        return selectedPointId

    def setTheLongSideOfArea(self):

        # choose the long side
        if self.selectedPointId == 0:
            dist1 = math.sqrt(math.pow(self.selectedPoints[0][0] - self.selectedPoints[1][0], 2) + math.pow(self.selectedPoints[0][1] - self.selectedPoints[1][1], 2))
            dist2 = math.sqrt(math.pow(self.selectedPoints[0][0] - self.selectedPoints[3][0], 2) + math.pow(self.selectedPoints[0][1] - self.selectedPoints[3][1], 2))

            if dist1 <= dist2:
                self.findAlignment(0, 3, 1)
                self.route = "0->3"
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(0, 1))

                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]

                self.setFirstTwoPoints(0, 3)


            else:
                self.findAlignment(0, 1, 3)
                self.route = "0->1"
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(0, 3))
                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]
                self.setFirstTwoPoints(0, 1)


        elif self.selectedPointId == 3:
            dist1 = math.sqrt(math.pow(self.selectedPoints[3][0] - self.selectedPoints[0][0], 2) + math.pow(self.selectedPoints[3][1] - self.selectedPoints[0][1], 2))
            dist2 = math.sqrt(math.pow(self.selectedPoints[3][0] - self.selectedPoints[2][0], 2) + math.pow(self.selectedPoints[3][1] - self.selectedPoints[2][1], 2))


            if dist1 <= dist2:
                self.findAlignment(3, 2, 0)

                self.route = "3->2"
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(3, 0))
                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]

                self.setFirstTwoPoints(3, 2)

            else:
                self.findAlignment(3, 0, 2)

                self.route = "3->0"
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(3, 2))
                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]

                self.setFirstTwoPoints(3, 0)

        else:
            dist1 = math.sqrt(math.pow(self.selectedPoints[self.selectedPointId][0] - self.selectedPoints[self.selectedPointId - 1][0], 2) + math.pow(self.selectedPoints[self.selectedPointId][1] - self.selectedPoints[self.selectedPointId - 1][1], 2))
            dist2 = math.sqrt(math.pow(self.selectedPoints[self.selectedPointId][0] - self.selectedPoints[self.selectedPointId + 1][0], 2) + math.pow(self.selectedPoints[self.selectedPointId][1] - self.selectedPoints[self.selectedPointId + 1][1], 2))

            if dist1 <= dist2:
                self.findAlignment(self.selectedPointId, self.selectedPointId + 1, self.selectedPointId-1)

                self.route = self.selectedPointId,"->",(self.selectedPointId + 1)
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(self.selectedPointId, self.selectedPointId - 1))
                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]

                self.setFirstTwoPoints(self.selectedPointId, self.selectedPointId + 1)

            else:
                self.findAlignment(self.selectedPointId, self.selectedPointId - 1, self.selectedPointId + 1)

                self.route = self.selectedPointId,"->",(self.selectedPointId - 1)
                self.totalWayPointNumber = (int) (2 * self.findTourNumber(self.selectedPointId, self.selectedPointId + 1))
                self.wayPoints = [[0] * 2 for _ in range(self.totalWayPointNumber)]

                self.setFirstTwoPoints(self.selectedPointId, self.selectedPointId - 1)
                

    def findTourNumber(self,selectedPoint,anotherPoint):
        return math.fabs(
            math.floor(
                ((self.selectedPoints[selectedPoint][0] - self.selectedPoints[anotherPoint][0]) + (
                            self.selectedPoints[selectedPoint][1] - self.selectedPoints[anotherPoint][1])) / 2.0
            )
        )

    def findAlignment(self,startingPointId, endingPointId, alignmentPoint):

        if self.selectedPoints[startingPointId][0] == self.selectedPoints[endingPointId][0]:
            self.isVertical = True

            # Vertical Route
            if self.selectedPoints[startingPointId][1] > self.selectedPoints[endingPointId][1]:
                self.isDown = True
            elif self.selectedPoints[startingPointId][1] < self.selectedPoints[endingPointId][1]:
                self.isUp = True

            if self.selectedPoints[startingPointId][0] > self.selectedPoints[alignmentPoint][0]:
                self.isLeft = True
            elif self.selectedPoints[startingPointId][0] < self.selectedPoints[alignmentPoint][0]:
                self.isRight = True

        elif self.selectedPoints[startingPointId][1] == self.selectedPoints[endingPointId][1]:
            self.isHorizontal = True

            # Horizontal Route
            if self.selectedPoints[startingPointId][0] > self.selectedPoints[endingPointId][0]:
                self.isLeft = True
            elif self.selectedPoints[startingPointId][0] < self.selectedPoints[endingPointId][0]:
                self.isRight = True

            if self.selectedPoints[startingPointId][1] > self.selectedPoints[alignmentPoint][1]:
                self.isDown = True
            elif self.selectedPoints[startingPointId][1] < self.selectedPoints[alignmentPoint][1]:
                self.isUp = True

    def redesignTheAlignmentFrstPnt(self):
        
        if self.isHorizontal:
            if self.isRight:
                self.wayPoints[1][0] -= 5 
            elif self.isLeft:
                self.wayPoints[1][0] += 5 
        elif self.isVertical:
            if self.isUp:
                self.wayPoints[1][1] -= 5 
            elif self.isDown:
                self.wayPoints[1][1] += 5 

    def setFirstTwoPoints(self, first, second):
        if self.isHorizontal:
            if self.isLeft:
                if self.isUp:
                    self.startingPoint[0] = self.selectedPoints[first][0] + self.necessaryDistToStartObserv
                    self.startingPoint[1] = self.selectedPoints[first][1] + self.maxDistanceForCamera

                    self.alignmentPoint[0] = self.selectedPoints[second][0] - self.necessaryDistToStartObserv
                    self.alignmentPoint[1] = self.selectedPoints[second][1] + self.maxDistanceForCamera

                    self.wayPoints[0][0] = self.startingPoint[0] + self.rotationAlignmentDistance
                    self.wayPoints[0][1] = self.startingPoint[1]

                    self.wayPoints[1][0] = self.alignmentPoint[0] - self.rotationAlignmentDistance
                    self.wayPoints[1][1] = self.alignmentPoint[1]

                    i = 2

                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i-1][0]
                            self.wayPoints[i][1] = self.wayPoints[i-1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i-3][0]
                            self.wayPoints[i][1] = self.wayPoints[i-3][1] + 2 * self.maxDistanceForCamera

                elif self.isDown:
                    self.startingPoint[0] = self.selectedPoints[first][0] + self.necessaryDistToStartObserv
                    self.startingPoint[1] = self.selectedPoints[first][1] - self.maxDistanceForCamera

                    self.alignmentPoint[0] = self.selectedPoints[second][0] - self.necessaryDistToStartObserv
                    self.alignmentPoint[1] = self.selectedPoints[second][1] - self.maxDistanceForCamera

                    self.wayPoints[0][0] = self.startingPoint[0] + self.rotationAlignmentDistance
                    self.wayPoints[0][1] = self.startingPoint[1]

                    self.wayPoints[1][0] = self.alignmentPoint[0] - self.rotationAlignmentDistance
                    self.wayPoints[1][1] = self.alignmentPoint[1]



                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera

            elif self.isRight:
                if self.isUp:
                    self.startingPoint[0] = self.selectedPoints[first][0] - self.necessaryDistToStartObserv
                    self.startingPoint[1] = self.selectedPoints[first][1] + self.maxDistanceForCamera

                    self.alignmentPoint[0] = self.selectedPoints[second][0] + self.necessaryDistToStartObserv
                    self.alignmentPoint[1] = self.selectedPoints[second][1] + self.maxDistanceForCamera

                    self.wayPoints[0][0] = self.startingPoint[0] - self.rotationAlignmentDistance
                    self.wayPoints[0][1] = self.startingPoint[1] 

                    self.wayPoints[1][0] = self.alignmentPoint[0] + self.rotationAlignmentDistance
                    self.wayPoints[1][1] = self.alignmentPoint[1]


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera

                elif self.isDown:
                    self.startingPoint[0] = self.selectedPoints[first][0] - self.necessaryDistToStartObserv
                    self.startingPoint[1] = self.selectedPoints[first][1] - self.maxDistanceForCamera

                    self.alignmentPoint[0] = self.selectedPoints[second][0] + self.necessaryDistToStartObserv
                    self.alignmentPoint[1] = self.selectedPoints[second][1] - self.maxDistanceForCamera

                    self.wayPoints[0][0] = self.startingPoint[0] - self.rotationAlignmentDistance
                    self.wayPoints[0][1] = self.startingPoint[1]

                    self.wayPoints[1][0] = self.alignmentPoint[0] + self.rotationAlignmentDistance
                    self.wayPoints[1][1] = self.alignmentPoint[1]


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera

        elif self.isVertical:
            if self.isUp:
                if self.isRight:
                    self.startingPoint[0] = self.selectedPoints[first][0] + self.maxDistanceForCamera
                    self.startingPoint[1] = self.selectedPoints[first][1] - self.necessaryDistToStartObserv

                    self.alignmentPoint[0] = self.selectedPoints[second][0] + self.maxDistanceForCamera
                    self.alignmentPoint[1] = self.selectedPoints[second][1] + self.necessaryDistToStartObserv

                    self.wayPoints[0][0] = self.startingPoint[0]
                    self.wayPoints[0][1] = self.startingPoint[1] - self.rotationAlignmentDistance


                    self.wayPoints[1][0] = self.alignmentPoint[0]
                    self.wayPoints[1][1] = self.alignmentPoint[1] + self.rotationAlignmentDistance


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0] + 2 * self.maxDistanceForCamera
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1]
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0] + 2 * self.maxDistanceForCamera
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1]


                elif self.isLeft:
                    self.startingPoint[0] = self.selectedPoints[first][0] - self.maxDistanceForCamera
                    self.startingPoint[1] = self.selectedPoints[first][1] - self.necessaryDistToStartObserv

                    self.alignmentPoint[0] = self.selectedPoints[second][0] - self.maxDistanceForCamera
                    self.alignmentPoint[1] = self.selectedPoints[second][1] + self.necessaryDistToStartObserv

                    self.wayPoints[0][0] = self.startingPoint[0]
                    self.wayPoints[0][1] = self.startingPoint[1] - self.rotationAlignmentDistance

                    self.wayPoints[1][0] = self.alignmentPoint[0]
                    self.wayPoints[1][1] = self.alignmentPoint[1] + self.rotationAlignmentDistance


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera


            elif self.isDown:

                if self.isRight:
                    self.startingPoint[0] = self.selectedPoints[first][0] + self.maxDistanceForCamera
                    self.startingPoint[1] = self.selectedPoints[first][1] + self.necessaryDistToStartObserv

                    self.alignmentPoint[0] = self.selectedPoints[second][0] + self.maxDistanceForCamera
                    self.alignmentPoint[1] = self.selectedPoints[second][1] - self.necessaryDistToStartObserv

                    self.wayPoints[0][0] = self.startingPoint[0]
                    self.wayPoints[0][1] = self.startingPoint[1] + self.rotationAlignmentDistance

                    self.wayPoints[1][0] = self.alignmentPoint[0]
                    self.wayPoints[1][1] = self.alignmentPoint[1] - self.rotationAlignmentDistance


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera

                elif self.isLeft:
                    self.startingPoint[0] = self.selectedPoints[first][0] - self.maxDistanceForCamera
                    self.startingPoint[1] = self.selectedPoints[first][1] + self.necessaryDistToStartObserv

                    self.alignmentPoint[0] = self.selectedPoints[second][0] - self.maxDistanceForCamera
                    self.alignmentPoint[1] = self.selectedPoints[second][1] - self.necessaryDistToStartObserv

                    self.wayPoints[0][0] = self.startingPoint[0] 
                    self.wayPoints[0][1] = self.startingPoint[1] + self.rotationAlignmentDistance

                    self.wayPoints[1][0] = self.alignmentPoint[0]
                    self.wayPoints[1][1] = self.alignmentPoint[1] - self.rotationAlignmentDistance


                    for i in range(2,len(self.wayPoints)):
                        if i % 2 == 0:
                            self.wayPoints[i][0] = self.wayPoints[i - 1][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 1][1] + 2 * self.maxDistanceForCamera
                        else:
                            self.wayPoints[i][0] = self.wayPoints[i - 3][0]
                            self.wayPoints[i][1] = self.wayPoints[i - 3][1] + 2 * self.maxDistanceForCamera
    
    def convertXY_To_RealLocations(self,location):
        
        # Australia => 55 
        # Istanbul => 35
        # Maras => 37

        if location == "Australia":
            self.latLonToXY("EPSG:32755")
        elif location == "Maras":
            self.latLonToXY("EPSG:32637")
        elif location == "Istanbul":        
            self.latLonToXY("EPSG:32635")

    # Convertion of lat. and long. of 4 specified points
    def latLonToXY(self,utm):
        crs_latlon = CRS("EPSG:4326")
        crs_utm = CRS(utm)

        transformer_to_utm = Transformer.from_crs(crs_latlon, crs_utm, always_xy=True)
        transformer_to_latlon = Transformer.from_crs(crs_utm, crs_latlon, always_xy=True)

        for i in range(4):
            self.selectedPoints[i][0], self.selectedPoints[i][1] = transformer_to_utm.transform(self.latLongCoordinatesOf4[i][1], self.latLongCoordinatesOf4[i][0])

    # Redesign the coordinates to make rectangle shape them
    def redesignTheCoordinates(self):

        if(self.selectedPoints[0][1] < self.selectedPoints[1][1]):
            self.selectedPoints[1][1] = self.selectedPoints[0][1]
        else:
            self.selectedPoints[0][1] = self.selectedPoints[1][1]

        
        if(self.selectedPoints[3][1] > self.selectedPoints[2][1]):
            self.selectedPoints[2][1] = self.selectedPoints[3][1]
        else:
            self.selectedPoints[3][1] = self.selectedPoints[2][1]


        if(self.selectedPoints[0][0] < self.selectedPoints[3][0]):
            self.selectedPoints[3][0] = self.selectedPoints[0][0]
        else:
            self.selectedPoints[0][0] = self.selectedPoints[3][0]    


        if(self.selectedPoints[1][0] > self.selectedPoints[2][0]):
            self.selectedPoints[2][0] = self.selectedPoints[1][0]
        else:
            self.selectedPoints[1][0] = self.selectedPoints[2][0]    


    def wayPointsConvertionFromXYToLatLong(self,location):

        utm = ""

        if(location == "Australia"):
            utm = "EPSG:32755"
        elif(location == "Maras"):
            utm = "EPSG:32637"
        elif(location == "Istanbul"):    
            utm = "EPSG:32635"

        crs_latlon = CRS("EPSG:4326")
        crs_utm = CRS(utm)

        transformer_to_latlon = Transformer.from_crs(crs_utm, crs_latlon, always_xy=True)

        self.wayPointsListAsLatLong = [[0] * 2 for _ in range(len(self.wayPoints))]

        self.wayPointsListAsLatLong[0][0] = self.referencePoint[0]
        self.wayPointsListAsLatLong[0][1] = self.referencePoint[1]

        for i in range(1,len(self.wayPoints)):

            self.wayPointsListAsLatLong[i][1], self.wayPointsListAsLatLong[i][0] = transformer_to_latlon.transform(self.wayPoints[i][0],self.wayPoints[i][1])
