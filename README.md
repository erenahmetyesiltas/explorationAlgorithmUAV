My algorithm's goal is exploring the specified region completely as soon as possible with an unmanned aerial vehicle.
Our UAV has a camera with this properties:
--> Vertical sight degree: 30
--> Horizontal sight degree: 60

In addition, the height we determined for the UAV to fly is 15 meters.
Also, we get the location data as longitude and latitude.

My algorithm includes several steps. I am explaining the significant steps one by one with the functions name in the code files respectively.

1. When our another program choose an area with rectangle it just takes 2 points diagonally.
   A function called **givenPointsTo4PointsCoordinates(self,givenPoints,sel4PointsCords)** converts the 2 diagonal points of a rectangle into the 4 points of this rectangle.

2. The starting point of the UAV is saved in the program with an array called **referencePoint**.

3. Doing computational operation in coordinate system is the one of the best option to compute geometrical, areal thing better. For this reason, we convert the longitutude and latitude to x and y
   with functions called **convertXY_To_RealLocations(self,location) and latLonToXY(self,utm)**. In these functions, locations(e.g. Australia, Istanbul, London) are must to state the correct values.

4. **step 3** the values came out cannot make a perfect rectangle. For this reason, I added a function called **redesignTheCoordinates(self):** to make a perfect rectangle.
   Some doubt can be thought here but the values came out from step3 is really close to the obtained values from the function. That is way, if the values are regulated in order to make a perfect rectangle, it does not cause a big problem. ![Conversion to Perfect Rectangle](https://github.com/erenahmetyesiltas/explorationAlgorithmUAV/blob/main/Conversion%20To%20Rectangle.png)

5. Above steps, the rectangles' 4 points are obtained. To make a flight with minimum time, the UAV should fly to the closest point to the its starting point. There is a function called **setTheClosestPoint** does it.

6. There is another point is that to get the minimum flight time, it should make minimum turn since unnecessary turn cause loss of time.
   For this reason, when the rectangle is thought, turnings in short side of rectangle cause loss of time less. In addition, I code the route along long side of the rectangle due to the reason.
   That is way, there is a function called **setTheLongSideOfArea** to find the long side. Moreover, the function find the short side in order to find the turning points is aligned along this direction ![Long Side vs Short Side Number of Turning Points](https://github.com/erenahmetyesiltas/explorationAlgorithmUAV/blob/main/Long%20Side%20vs%20Short%20Side%20Number%20of%20Turning%20Points.png). The function includes other important methods(Find the how the route will be, how many turning points will be obtained and their location). You can see it from my code files.

7. After the function **setTheLongSideOfArea** we can get the points as x and y values. To be able to use them in the real world I converted it to longitude and latitude with the function **.wayPointsConvertionFromXYToLatLong(location)**. In this way, the necessary coordinates are acquired.

8. I added the some important calculations about finding the points of the route of the UAV. You can examine them.
   ![UAV's Camera's Horizontal Calculations](https://github.com/erenahmetyesiltas/explorationAlgorithmUAV/blob/main/UAV%20Horizontal%20Calculation%20Things.png)
   ![UAV's Camera's Vertical Calculations](https://github.com/erenahmetyesiltas/explorationAlgorithmUAV/blob/main/UAV%20Vertical%20Calculation%20Things.png)
