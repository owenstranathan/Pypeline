'''
    PypeGraph.py defines the underlying functionality
    behind the pretty graphics of the GUI
    The PypeGraph.py simply defines a modifiable
    unidirectional graph using an adjacency list
    A graph is a data structure composed of nodes and edges,

    in this implementation:

    a NODE is:
        a list of edges
        a unique lable
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
class Node():
    def __init__(self, pos, lable):
        self.lable = lable
        self.pos = pos #a position on the cartesian plane
        self._neighbors = []  ##an empty list to hold edges, named neighbors
        ##MORE...

    ##adds edge if it is not a duplicate
    def addEdge(self, node, weight = 1):
        for edge in self._neighbors:
            if edge.node.lable == node.lable or edge.node.pos == node.pos:
                return False
        print "node: ", self.lable, " is getting neighbor: ", node.lable
        self._neighbors.append(Edge(node, weight))
        return True

###############################################################################
##EDGE#########################################################################
###############################################################################

class Edge():
    def __init__(self, node, weight):
        self.node = node ##a neighboring node
        self.weight = weight ##a weight of the edge (i.e. distance from node to node)
        ##MORE...

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
        the graph will auto lable the graph if the lable argument given
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
        ##a private integer for automatic id assignment
        self._node_id = 0


    ##to add a new node simply append a new node to the node list
    ##returns true if the node was added
    ##false if contract(1) of graph were broken
    def addNode(self, pos,  lable=-1):
        for node in self.nodes:
            if node.pos == pos or node.lable == lable:
                print "cannont add node"
                return False
        print "nodes is gettin added"
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
    def deleteNode(self, lable):
        ##examine every node in the list
        for node in self.nodes:
            ##if the node is found then remove it from the graph
            if node.lable == lable:
                self.nodes.remove(node)
            else:
                ##also look for the node in the edges of other nodes
                for edge in node._neighbors:
                    ##and remove that edge if it exists
                    if edge.node.lable == lable:
                        node._neighbors.remove(edge)

        ##reset the focus node if necessary
        if self.focus_node.lable == lable:
            if not self.nodes:
                print "graph empty"
            else:
                self.focus_node = self.nodes[-1]

    #########################################
    ##for finding a node by lable			#
    def findNode(self, lable):				#
        for node in self.nodes:				#
            if node.lable == lable:			#
                return node					#
                                            #	A findNode function for
    ##for finding a node by pos				#	both lable and position is
    def findNode(self, pos):				#	unnessecary because
        for node in self.nodes:				#	two individual nodes
            if node.pos == pos:				#	should never have
                return node					#	the same position
    #########################################

    ##set focus given position
    def setFocus(self, pos):
        print pos
        self.focus_node = self.findNode(pos)

    ##set focus given position
    def setFocus(self, lable):
        self.focus_node = self.findNode(lable)

    ##resets the focus to the last node in the list
    def resetFocus(self):
        self.focus_node = self.nodes[-1]

    def pop(self):
        ##stash the node you are about to remove
        deadNode = self.nodes[-1]
        ##delete the node
        self.deleteNode(self.nodes[-1].lable)
        ##return the nead node
        return deadNode

    ##prints the adjacency list to the console
    def printGraph():
        for node in self.graph.nodes:
            neighbors = [neighbor.node.lable for neighbor in node._neighbors]
            print node.lable, neighbors

###############################################################################
##DRAW GRAPH###################################################################
###############################################################################


'''Global variables'''

GRAPH_HEIGHT = 640
GRAPH_WIDTH = 800
GRAPH_SIZE = (GRAPH_WIDTH, GRAPH_HEIGHT)
NODE_SIZE = 10


class DrawingGraph(Graph):
    def __init__(self):
            Graph.__init__(self)

    ##this uses BFT(breadth first traversal) to draw every node and
    ##edge in the graph
    def draw(self,Canvas):
        for node in self.nodes:
            Canvas.AddCircle(
                node.pos,
                10,
                LineWidth=1,
                LineColor='Black',
                FillColor='Black'
            )
            for edge in node._neighbors:
                line = (node.pos, edge.node.pos)
                Canvas.AddArrowLine(
                    line, LineWidth=2,
                    LineColor="Red",
                    ArrowHeadSize=16
                )
