'''
    PypeGraph.py defines the underlying functionality
    behind the pretty graphics of the GUI
    The PypeGraph.py simply defines a modifiable
    unidirectional graph using an adjacency list
    A graph is a data structure composed of nodes and edges,

    in this implementation:

    a NODE is:
        a list of edges
        a unique label
        an X coordinate
        a Y coordinate
        #other pipeline network engineery stuff

    an EDGE is:
        a single node
        an edge weight(length)
        #other pipeline network engineery stuff

'''
###############################################################################
##NODE#########################################################################
###############################################################################
'''
CONTRACTS:
    1)
        duplicate edges are disallowed
'''
from wx.lib.floatcanvas import FloatCanvas
import Geometry as Geom
import math

class Node():
    def __init__(self, pos, label):
        self.label = label
        self.pos = pos #a position on the cartesian plane
        self._neighbors = []  ##an empty list to hold edges, named neighbors

        ##MORE...

    ##adds edge if it is not a duplicate
    def addEdge(self, node, weight = 1):
        for edge in self._neighbors:
            if edge.node.label == node.label or edge.node.pos == node.pos:
                return False
        self._neighbors.append(Edge(node, weight))
        return True

    def removeEdge(self, arg_edge):
        ## look for the edge
        for edge in self._neighbors:
            ## if you find it then remove it
            if edge is arg_edge:
                self._neighbors.remove(arg_edge)
                return True

        ## if you don't find it then return false
        return False

###############################################################################
##EDGE#########################################################################
###############################################################################

class Edge():
    def __init__(self, node, weight):
        self.node = node ##a neighboring node
        self.weight = weight ##a weight of the edge (i.e. distance from node to node)
        self.line = None

        ##MORE...
        self.elements = []

    def setLine(self, new_line):
        self.line = new_line


    def addElement(self, arg_element):
        for element in self.elements:
            if element.pos == arg_element.pos:
                print "Cannot add element at this position"
                return False

        self.elements.append(arg_element)
        return True

###############################################################################
##EDGE ELEMENT#################################################################
###############################################################################
## the Edge element is a parent class for
## Valve, Compressors, Regulators and Loss Elements
## it's Comstrutor takes a position tuple( x, y) coordinate
## and a flow switch (a positive or negative number (+1/-1) to signify
## the direction of flow on the Edge(pipe) )
class EdgeElement():
    def __init__(self, pos):
        self.pos = pos



class Valve(EdgeElement):
    def __init__(self, pos):
        EdgeElement.__init__(self, pos)

    def draw(self, Canvas, line):
        t_size =  8 / Canvas.Scale
        point = self.pos
        ## Make the T shape with lines
        downPoint = (point[0] , point[1]-t_size/2)
        upPoint = (point[0], point[1]+t_size)
        rightPoint = (point[0]+t_size, point[1]+t_size)
        leftPoint = (point[0]-t_size, point[1]+t_size)

        ## rotate the T shape to always be normal to the edge
        theta = Geom.angleFromXaxis(line)
        lines = [leftPoint, rightPoint , upPoint, downPoint]
        lines = Geom.rotatePointList(lines, theta, point)


        Canvas.AddLine(
            [lines[0], lines[1]],
            LineWidth=4,
            LineColor="BLUE"
        )
        Canvas.AddLine(
            [lines[2], lines[3]],
            LineWidth=4,
            LineColor="BLUE"
        )


class Compressor(EdgeElement):
    def __init__(self, pos):
        EdgeElement.__init__(self, pos)

    def draw(self, Canvas, line):
        c_w = 10 / Canvas.Scale
        c_h_long = 10 /Canvas.Scale
        c_h_short = 3 / Canvas.Scale
        point = self.pos
        leftPoint = (point[0]-c_w, point[1])
        rightPoint = (point[0]+c_w, point[1])



        def rightCompressor(l_point, r_point):
            upLeftPoint = (l_point[0], l_point[1]+c_h_long)
            downLeftPoint = (l_point[0], l_point[1]-c_h_long)
            upRightPoint = (r_point[0], r_point[1]+c_h_short)
            downRightPoint = (r_point[0], r_point[1]-c_h_short)
            return [upLeftPoint, downLeftPoint, downRightPoint, upRightPoint]

        def leftCompressor(l_point, r_point):
            upLeftPoint = (l_point[0], l_point[1]+c_h_short)
            downLeftPoint = (l_point[0], l_point[1]-c_h_short)
            upRightPoint = (r_point[0], r_point[1]+c_h_long)
            downRightPoint = (r_point[0], r_point[1]- c_h_long)
            return [upLeftPoint, downLeftPoint, downRightPoint, upRightPoint]


        ## find the change in x on the line to determine the
        ## direction of the edge
        delta_x = Geom.delta_x(*line)

        ## get the angle that the line makes with the x-axis
        theta = Geom.angleFromXaxis(line)

        ## if it's negative the direction in the x is right justified
        if delta_x < 0:
            ## so we construct a right justified shape
            compressor = rightCompressor(leftPoint, rightPoint)

        ## if it's positive the direction in the x is left justified
        elif delta_x > 0:
            ## so we construct a left justified shape
            compressor = leftCompressor(leftPoint, rightPoint)

        ## Uh Oh Vertical lines, now we have to think about the change in y
        elif delta_x == 0:
            ## the change in y
            delta_y = Geom.delta_y(*line)

            ## if it's positive then the direction in the y is up
            if delta_y < 0:
                ## since we will ultimately be rotating 90 degrees
                ## for a vertical line pointing up
                ## we want the shape to be right justified
                ## (think about it)
                compressor = rightCompressor(leftPoint, rightPoint)

            ##if it's negative then the direction in the y is down
            elif delta_y > 0:
                ## and we construct a left justified shape
                compressor = leftCompressor(leftPoint, rightPoint)

        ## if the delta y is also zero then our line is two of
        ## the same point and we have some bad input
        ## since this code is just for prototyping and fast development
        ## we will make due with a descriptive warning message printed
        ## to the console, and we'll make compressor right justified
        ## don't worry if this happens it will be obvious
        else:
            compressor = rightCompressor(leftPoint, rightPoint)


        ## and then we rotate it acordingly
        compressor = Geom.rotatePointList(compressor, theta, point)

        ## finally we draw this darned thing to the Canvas
        Canvas.AddPolygon(
            compressor,
            LineWidth=1,
            LineColor="BLUE",
            FillColor="BLUE",
        )

class Regulator(EdgeElement):
    def __init__(self, pos):
        EdgeElement.__init__(self, pos)

    def draw(self, Canvas, line):
        r_size = 10 / Canvas.Scale
        point = self.pos
        rightPoint = (point[0] - r_size, point[1])
        leftPoint = (point[0] + r_size, point[1])
        upRightPoint = (rightPoint[0], rightPoint[1]+ r_size)
        downRightPoint = (rightPoint[0], rightPoint[1]-r_size)
        upLeftPoint = (leftPoint[0], leftPoint[1]+r_size)
        downLeftPoint = (leftPoint[0], leftPoint[1]-r_size)

        theta = Geom.angleFromXaxis(line)

        firstTriangle = [point, upRightPoint, downRightPoint]
        secondTriangle = [point, upLeftPoint, downLeftPoint]

        firstTriangle = Geom.rotatePointList(firstTriangle, theta, point)
        secondTriangle = Geom.rotatePointList(secondTriangle, theta, point)


        Canvas.AddPolygon(
            firstTriangle,
            LineWidth=1,
            LineColor="BLUE",
            FillColor="BLUE",
        )
        Canvas.AddPolygon(
            secondTriangle,
            LineWidth=1,
            LineColor="BLUE",
            FillColor="BLUE",
        )

class LossElement(EdgeElement):
    def __init__(self, pos):
        EdgeElement.__init__(self, pos)


    def draw(self, Canvas, line):
        l_size = 8 / Canvas.Scale
        point = self.pos
        upPoint = (point[0], point[1]+ l_size)
        downPoint = (point[0], point[1] - l_size)
        rightPoint = (point[0] + l_size, point[1] - l_size)
        lines = [upPoint, downPoint, rightPoint]
        theta = Geom.angleFromXaxis(line)
        lines = Geom.rotatePointList(lines, theta, point)
        Canvas.AddLine(
            [lines[0], lines[1]],
            LineWidth=4,
            LineColor="BLUE"
        )
        Canvas.AddLine(
            [lines[1], lines[2]],
            LineWidth=4,
            LineColor="BLUE"
        )

###############################################################################
##GRAPH########################################################################
###############################################################################

'''
    This is the graph structure
    and these are it's contracts
    CONTRACTS:
    1)
        the graph disallows adding duplicate nodes
    2)
        the graph will auto label the graph if the label argument given
        to addNode is equal to -1, which it is by default
    3)
        if the focus node is deleted the focus node becomes
        the last node in the list
'''

class Graph():
    def __init__(self):
        ##an empty list of nodes ( the adjacency list )
        self.nodes = []

        ##a node variable for node focus (the node being looked at)
        self.focus_node = None
        ##an Edge variable to hold the focus edge
        self.focus_edge = None
        ##a private integer for automatic id assignment
        self._node_id = 0

        ##undo history so that you can redo
        self.undone_nodes = []



    ##to add a new node simply append a new node to the node list
    ##returns true if the node was added
    ##false if contract(1) of graph were broken
    def addNode(self, pos,  label=-1):
        for node in self.nodes:
            if node.pos == pos or node.label == label:
                print "cannot add node"
                return False
        self.nodes.append(Node(pos, self._node_id))
        self._node_id += 1
        return True

    def addNodeDirectly(self, arg_node):
        for node in self.nodes:
            if node is arg_node:
                return False
        self.nodes.append(arg_node)
        return True



    ##deleting a node is alittle more complicated
    ##useing something similar to BFT
    ##python is weird and my c++ brain doesn't understand
    def deleteNode(self, arg_node):
        ##delete the node from the nodes list
        self.nodes.remove(arg_node)

        for node in self.nodes:
            ##also look for the node in the edges of other nodes
            for edge in node._neighbors:
                ##and remove that edge if it exists
                if edge.node is arg_node:
                    node._neighbors.remove(edge)

        ##reset the focus node
        if not self.nodes:
            print "graph empty"
            self.focus_node = None
        else:
            self.focus_node = self.nodes[-1]

    def deleteEdge(self, arg_edge):
        for node in self.nodes:
            ## try and remove an edge from all nodes
            if node.removeEdge(arg_edge):
                ##if you did it then good job; return True
                self.printGraph()
                return True
        ## if you don't find it then return False
        return False


    def hasEdge(self, arg_node):
        ## if the _neighbors list is not empty
        if arg_node._neighbors:
            ## the node definately has edges
            return True
        ## look for hte node in everyone else's neighbors
        else:
            for node in self.nodes:
                for edge in node._neighbors:
                    if edge.node is arg_node:
                        return True

        ## if you find no edge then return Falsch
        return False

    #########################################
    ##for finding a node by label			#
    def findNodeByLable(self, label):		        #
        for node in self.nodes:				#
            if node.label == label:			#
                return node                 #
        return None             			#
                                            #	A findNode function for
    ##for finding a node by pos				#	both label and position is
    def findNodeByPos(self, pos):				#	unnessecary because
        for node in self.nodes:				#	two individual nodes
            if node.pos == pos:				#	should never have
                return node	                #	the same position
        return None         				#
    #########################################

    ##set focus given position
    def setFocusByPos(self, pos):
        self.focus_node = self.findNodeByPos(pos)

    ##set focus given position
    def setFocusByLable(self, label):
        self.focus_node = self.findNodeByLable(label)

    ##resets the focus to the last node in the list
    def resetFocus(self):
        self.focus_node = self.nodes[-1]
        self.printGraph()

    def pop(self):
        ##stash the node you are about to remove
        deadNode = self.nodes[-1]
        ##delete the node
        self.deleteNode(self.nodes[-1].label)
        ##return the nead node
        return deadNode

    ##prints the adjacency list to the console
    def printGraph(self):
        print "----------------------------------------------------------------"
        for node in self.nodes:
            neighbors = [neighbor.node.label for neighbor in node._neighbors]
            print node.label, node.pos, "   ", neighbors
        print "----------------------------------------------------------------"


    def undo(self):
        ##if the graph is empty do nothing
        if not self.nodes:
            print "nothing to undo"
            return
        ##other wise
        else:
            ##push the last node added to the graph onto the
            ##undo history stack
            ##I say stack because that's really what it is
            ##it's a list that practices last in first out
            ##i.e. a stack
            self.undone_nodes.append(self.pop())
            if not self.nodes:
                self.firstClick = False
            else:
                self.resetFocus()


    ##redoes undone nodes
    def redo(self):
        ##if the list is empty do nothing
        if not self.undone_nodes:
            print "nothing to redo"
            return
        ##other wise grab the last node in the undo history
        else:
            zombieNode = self.undone_nodes.pop()
            ##try and add that node to the graph
            ##there should never be a problem here but we made
            ##addNode return bool so we should use it
            if not self.addNodeDirectly(zombieNode):
                print "cannot add node"
                return
            ##if you can add it
            else:
                ##try and make the edge
                ##this might have a fail condition but##not one that I can think
                ##of, maybe you're smarter than me ;)
                if not self.focus_node.addEdge(zombieNode):
                    print "cannot add edge"
                    return
                ##if that's successfull(it should be)
                ##then reset the focus
                ##and the current pos
                else:
                    print self.focus_node.label
                    self.resetFocus()
                    print self.focus_node.label


    def getEdgeFromPoint(self, point, margin=8):
        for node in self.nodes:
            for edge in node._neighbors:
                distance = Geom.distFromLineSeg(edge.line, point)
                if distance  <= margin:
                    return edge
        return None



    ##this uses BFT(breadth first traversal) to draw every node and
    ##edge in the graph
    def draw(self, Canvas):
        NODE_SIZE = 10 /Canvas.Scale ##the physical size of the node as drawn on the canvas
        LINE_SIZE = 4 #* Canvas.Scale

        #this adds lines and circles to the graph
        for node in self.nodes:
            for edge in node._neighbors:
                line = (node.pos, edge.node.pos)
                edge.setLine(line)
                if edge is self.focus_edge:
                    Canvas.AddLine(
                        line, LineWidth=LINE_SIZE + 8,
                        LineColor = "YELLOW"
                        #ArrowHeadSize=16
                    )

                Canvas.AddLine(
                    line, LineWidth=LINE_SIZE,
                    LineColor="BLACK"
                    #ArrowHeadSize=16
                )
                for element in edge.elements:
                    element.draw(Canvas, edge.line)
                    # Canvas.AddRectangle(
                    #     element.pos,
                    #     (5,5),
                    #     LineStyle="Solid",
                    #     LineWidth=2,
                    #     LineColor="Blue",
                    #     FillColor="Blue"
                    #     )


        for node in self.nodes:
            if node is self.focus_node:
                Canvas.AddCircle(
                    node.pos,
                    NODE_SIZE + 6,
                    LineWidth=1,
                    LineColor='YELLOW',
                    FillColor='YELLOW'
                )

            Canvas.AddCircle(
                node.pos,
                NODE_SIZE,
                LineWidth=1,
                LineColor='BLACK',
                FillColor='BLACK'
            )
        # ##This just puts a dotted square around the focus node
        # if self.focus_node:
        #     focus_box_wh = (NODE_SIZE + 5, NODE_SIZE + 5 )
        #     focus_box_pos = (
        #         self.focus_node.pos[0]-(NODE_SIZE+5)/2 ,
        #         self.focus_node.pos[1] - (NODE_SIZE+5)/2 )
        #     Canvas.AddRectangle(
        #         focus_box_pos,
        #         focus_box_wh,
        #         LineStyle="Dot",
        #         LineWidth=2,
        #         LineColor='BLACK'
        #         )
