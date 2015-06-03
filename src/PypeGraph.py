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
        print "node: ", self.label, " is getting neighbor: ", node.label
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
                print "cannont add node"
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
    def deleteNode(self, label):
        ##examine every node in the list
        for node in self.nodes:
            ##if the node is found then remove it from the graph
            if node.label == label:
                self.nodes.remove(node)
            else:
                ##also look for the node in the edges of other nodes
                for edge in node._neighbors:
                    ##and remove that edge if it exists
                    if edge.node.label == label:
                        node._neighbors.remove(edge)

        ##reset the focus node if necessary
        if self.focus_node.label == label:
            if not self.nodes:
                print "graph empty"
            else:
                self.focus_node = self.nodes[-1]

    #########################################
    ##for finding a node by label			#
    def findNode(self, label):				#
        for node in self.nodes:				#
            if node.label == label:			#
                return node					#
                                            #	A findNode function for
    ##for finding a node by pos				#	both label and position is
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
    def setFocus(self, label):
        self.focus_node = self.findNode(label)

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
            print node.label, neighbors
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
