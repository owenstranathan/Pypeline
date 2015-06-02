'''
        This is PypeGraph.py
        PypeGraph uses the Graph structure defined in Pypeline.py
        an wxPython/FloatCanvas to create a drawing
        surface for creating a pipeline network model

        further more it defines drawing utilies for
        a graphically representing a graph

        ##contracts
'''
import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas
import PypeGraph as PypeGraph


'''Global variables'''

GRAPH_HEIGHT = 640
GRAPH_WIDTH = 800
GRAPH_SIZE = (GRAPH_WIDTH, GRAPH_HEIGHT)
NODE_SIZE = 10
grid_cell_size = 30


def getSnapPos( arg_pos):
    return (
        grid_cell_size* round(arg_pos[0]/grid_cell_size),
        grid_cell_size*round(arg_pos[1]/grid_cell_size)
        )


###############################################################################
##UI GRAPH#####################################################################
###############################################################################


class UIGraph(PypeGraph.Graph, wx.Frame):
    def __init__(self, parent, id, title, position, size):
        wx.Frame.__init__(self, parent, id, title, position, size)
        PypeGraph.Graph.__init__(self)
        self.InitUI()
        ##undo history so that you can redo
        self.undone_nodes = []
        ##CHANGE TO INITIALIZE WITH TOOLBAR BUTTON
        self.firstClick = False

        ##BIND MOUSE EVENTS
        self.Canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onLeftDown)
        self.Canvas.Bind(FloatCanvas.EVT_MOTION, self.onMouseMove)
        ##BIND KEYBOARD EVENTS
        self.Canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        ## BIND CHAR EVENT
        self.Canvas.Bind(wx.EVT_CHAR, self.onCharEvent)



    def InitUI(self):
        self.Canvas = NavCanvas.NavCanvas(self, -1,
                             size=(500, 500),
                             ProjectionFun=None,
                             Debug=0,
                             BackgroundColor="White",
                             ).Canvas

        # InitAll() sets everything in the Canvas to default state.
        # It can be used to reset the Canvas
        self.Canvas.InitAll()

        self.SetSize((GRAPH_WIDTH, GRAPH_HEIGHT))
        self.SetTitle('ASRAD Ueber Alles')
        self.Canvas.ZoomToBB()
        self.Centre()
        self.Show()

    def undo(self, coords):
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
        #because state has likely changes we ReDraw
        self.draw()

    ##redoes undone nodes
    def redo(self, coords):
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

        #because state has likely changes we ReDraw
        self.draw()


    ##LEFT CLICK EVENT HANDLER
    def onLeftDown(self, event):
        ##skip the event
        event.Skip()
        ##get the position of the click
        current_pos = getSnapPos(event.GetCoords())
        ##if this is the first click
        if self.firstClick is False:
            self.firstClick = True
            ##if there is already an node at the position in the graph
            if not self.addNode(current_pos):
                self.setFocus(current_pos)

            self.setFocus(current_pos)

        ##otherwise it's the second click
        else:
            ##first add a node to the graph
            if not self.addNode(current_pos):
                ##if there is already a node at that position then retreave it
                newNode = self.findNode(current_pos)
            else:
                newNode = self.nodes[-1]

            ##then create an edge between the this node and the focus node
            if not self.focus_node.addEdge(newNode):
                ##if the edge exists then return
                print "CANNOT ADD DUPLICATE EDGE"
                return

            else:
                self.setFocus(current_pos)

        ##if some nodes have recently been undone and you are creating new nodes
        if self.undone_nodes:
            ##officially delete the undone nodes
            del self.undone_nodes[:]

        #because state has likely changes we ReDraw
        self.draw

    ##Handle Character Events
    def onCharEvent(self,event):
        event.Skip()
        ctrlDown = event.CmdDown()
        keyCode = event.GetKeyCode()
        ##is ctrl and 'Y' pressed
        if ctrlDown and keyCode is 89:
            self.redo(getSnapPos(event.GetPosition()))
        ##is ctrl and 'Z' presed
        elif ctrlDown and keyCode is 90:
            self.undo(getSnapPos(event.GetPosition()))

        #because state has likely changes we ReDraw
        self.draw
        ##other stuff

    def onMouseMove(self, event):
        event.Skip()
        if self.firstClick:
            self.drawMotion(event)

        ##other stuff


    def onKeyDown(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
           self.firstClick = False
           ##because of state change we draw
           #self.draw()
        event.Skip()

    ##to draw mouse movement between clicks
    def drawMotion(self, event):
        self.newPos = getSnapPos(event.GetCoords())
        coords = (self.focus_node.pos , self.newPos)
        self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
        #we draw the graoh here because the state has most probably changed
        self.draw()

    ##this uses BFT(breadth first traversal) to draw every node and
    ##edge in the graph
    def drawGraph(self):
        for node in self.nodes:
            self.Canvas.AddCircle(
                node.pos,
                10,
                LineWidth=1,
                LineColor='BLACK',
                FillColor='BLACK'
            )
            for edge in node._neighbors:
                line = (node.pos, edge.node.pos)
                self.Canvas.AddArrowLine(
                    line, LineWidth=2,
                    LineColor="RED",
                    ArrowHeadSize=16
                )


    def draw(self):
        self.Canvas.Draw()
        self.Canvas.ClearAll()
        self.drawGraph()
