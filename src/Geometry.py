import math
###############################################################################
##GEOMETRY#####################################################################
###############################################################################

def delta_x(p1, p2):
    return p1[0] - p2[0]


def delta_y(p1,p2):
    return p1[1]-p2[1]


def slope(line):
    dx = delta_x(line[0], line[1])
    dy = delta_y(line[0], line[1])
    if dx == 0:
        return float("NaN")
    elif dy == 0:
        return float(0)
    else:
        return float(dy/dx)

def angleFromXaxis(line):
    m = slope(line)
    if math.isnan(m):
        ## we have a vertical line
        return math.radians(90)
    elif m == 0:
        return math.radians(0)
    else:
        return math.atan(m)


def rotatePoint(centerPoint,point,angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point


def rotatePointList(points, theta=math.pi, pointOfRotation=(0,0)):
    """Rotates the given polygon which consists of corners represented as (x,y),
    around a given point, counter-clockwise, theta degrees"""
    rotatedPoints = []
    for corner in points :
        rotatedPoints.append(rotatePoint(pointOfRotation, corner, theta))
    return rotatedPoints

## this function just returns the distance between two lines
def dist(point1, point2):
    Ax = point1[0]
    Ay = point1[1]
    Bx = point2[0]
    By = point2[1]

    return ((Bx-Ax)**2 + (By-Ay)**2)**0.5

##this function returns True if the point is in the domain of the
##line segment and false otherwise
def isInDomain(line, point):
    Ax = line[0][0]
    Ay = line[0][1]
    Bx = line[1][0]
    By = line[1][1]

    Cx = point[0]
    Cy = point[1]

    x_range = (min(Ax,Bx),max(Ax,Bx))

    if Cx > x_range[0]+5 and Cx < x_range[1]-5:
        return True
    else:
        return False

##this function returns True if the point is in the range of the
##line segment, and False otherwise
def isInRange(line, point):
    Ax = line[0][0]
    Ay = line[0][1]
    Bx = line[1][0]
    By = line[1][1]

    Cx = point[0]
    Cy = point[1]

    y_range = (min(Ay,By),max(Ay,By))

    if Cy > y_range[0]+5 and Cy < y_range[1]-5:
        return True
    else:
        return False

##this function returns the (shortest)distance from point to line
##if the point is not in the line segment's domain or range then
##the function returns 1000 as the distance
def distFromLineSeg( line, point):
    Ax = line[0][0]
    Ay = line[0][1]
    Bx = line[1][0]
    By = line[1][1]
    Cx = point[0]
    Cy = point[1]

    ##difference in y's
    delta_y = (Ay-By)
    #difference in x's
    delta_x = (Ax-Bx)
    distance = 1000
    '''
        there are three cases here:
        (1)
            the line given as an argument is Vertical
        (2)
            the line given as an argument is Horizontal
        (3)
            the line given as an Argument is neither Vertical nor Horizontal
    '''
    ##Case 1
    if delta_x == 0:
        if isInRange(line,point):
            distance = abs(Ax - Cx)
    ##Case 2
    elif delta_y == 0:
        if isInDomain(line, point):
            distance = abs(Ay-Cy)
    ##Case 3
    else:
        if isInRange(line,point):
            if isInDomain(line, point):

                ##Slope of the line
                line_m = (Ay-By)/(Ax-Bx)

                ##Y-intercept of the line
                line_b = Ay - (line_m*Ax)

                ##slope a perpendicular line is
                ##the negative inverse of the slope of the line
                perp_m = -1/line_m


                ##the y-intercept of the perpendicular line
                ##that contains the point argument(C)
                perp_b = Cy - (perp_m*Cx)

                ##the x coordinate of the intersection point
                ##between the line argument and the aforefound
                ##perpendicular line
                '''
                proof:
                    we want x givenequations of two lines

                    line 1:
                        y = (line_m * x) + line_b
                    line 2:
                        y = (perp_m * x) + perp_b

                    So we use algebra skills
                    =>
                        (line_m * x) + line_b = (perp_m * x) + perp_b
                    =>
                        (line_m * x) - (perp_m * x) = perp_b - line_b
                    =>
                        x* (line_m - perp_m) = (perp_b - line_b)
                    =>
                        x = (perp_b - line_b) / (line_m - perp_m)

                BOOM(...math...)
                '''
                Dx = (perp_b - line_b) / (line_m - perp_m)
                ##get the y-coordinate of the same point
                Dy = (perp_m*Dx) + perp_b

                ##Now all we do is find and return the distance(the shortest distance)
                distance = dist((Dx,Dy),(Cx,Cy))
    return distance



def snapPointToLine(line, point):
    Ax = line[0][0]
    Ay = line[0][1]
    Bx = line[1][0]
    By = line[1][1]
    Cx = point[0]
    Cy = point[1]

    ##difference in y's
    delta_y = (Ay-By)
    #difference in x's
    delta_x = (Ax-Bx)
    '''
        there are three cases here:
        (1)
            the line given as an argument is Vertical
        (2)
            the line given as an argument is Horizontal
        (3)
            the line given as an Argument is neither Vertical nor Horizontal
    '''
    ##Case 1
    if delta_x == 0:
        if isInRange(line,point):
            return (Ax, Cy)
    ##Case 2
    elif delta_y == 0:
        if isInDomain(line, point):
            return (Cx, Ay)
    ##Case 3
    else:
        if isInRange(line,point):
            if isInDomain(line, point):

                ##Slope of the line
                line_m = (Ay-By)/(Ax-Bx)

                ##Y-intercept of the line
                line_b = Ay - (line_m*Ax)

                ##slope a perpendicular line is
                ##the negative inverse of the slope of the line
                perp_m = -1/line_m


                ##the y-intercept of the perpendicular line
                ##that contains the point argument(C)
                perp_b = Cy - (perp_m*Cx)

                ##the x coordinate of the intersection point
                ##between the line argument and the aforefound
                ##perpendicular line
                '''
                proof:
                    we want x givenequations of two lines

                    line 1:
                        y = (line_m * x) + line_b
                    line 2:
                        y = (perp_m * x) + perp_b

                    So we use algebra skills
                    =>
                        (line_m * x) + line_b = (perp_m * x) + perp_b
                    =>
                        (line_m * x) - (perp_m * x) = perp_b - line_b
                    =>
                        x* (line_m - perp_m) = (perp_b - line_b)
                    =>
                        x = (perp_b - line_b) / (line_m - perp_m)

                BOOM(...math...)
                '''
                Dx = (perp_b - line_b) / (line_m - perp_m)
                ##get the y-coordinate of the same point
                Dy = (perp_m*Dx) + perp_b

                return (Dx,Dy)
