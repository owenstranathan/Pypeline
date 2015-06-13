
###############################################################################
##GEOMETRY#####################################################################
###############################################################################

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

    if Cx >= x_range[0] and Cx <= x_range[1]:
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

    if Cy >= y_range[0] and Cy <= y_range[1]:
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
                distance = ((Dx-Cx)**2 + (Dy-Cy)**2)**0.5
    return distance
