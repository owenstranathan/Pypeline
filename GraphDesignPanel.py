'''
        This is GraphDesignPanel.py
        PypeGraph uses the Graph structure defined in PypeGraph.py
        and wxPython/FloatCanvas to create a drawing
        surface for creating a pipeline network model

        further more it defines drawing utilities for
        graphically representing and otherwise manipulating a graph


'''
import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, GUIMode, Resources


'''Global variables'''

GRAPH_HEIGHT = 640
GRAPH_WIDTH = 800
GRAPH_SIZE = (GRAPH_WIDTH, GRAPH_HEIGHT)
NODE_SIZE = 10
grid_cell_size = 30


def getSnapPos(arg_pos):
    return (
        grid_cell_size* round(arg_pos[0]/grid_cell_size),
        grid_cell_size*round(arg_pos[1]/grid_cell_size)
        )

##EDIT
##We are going to use the floatcanvas way of making GUIModes to switch
##between different ways of handling input(events)
##this is actually good OOP design because we are encapsulating
##behaviors within the larger Design panel class

'''
    GUI Modes for DesignPanel
'''

"""
DESIGN:
    THIS GUI MODE IS FOR ADDING NODES AND OTHERWIZE EXTENDING THE GRAPH
"""
class GUIAddNodes(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph
        self.firstClick = False

    def OnLeftDown(self, event):
        ##get the position of the click
        current_pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
        ##if this is the first click
        if self.firstClick is False:
            self.firstClick = True
            ##if there is already an node at the position in the graph
            if not self.graph.addNode(current_pos):
                self.graph.setFocusByPos(current_pos)

            self.graph.setFocusByPos(current_pos)

        ##otherwise it's the second click
        else:
            ##first add a node to the graph
            if not self.graph.addNode(current_pos):
                ##if there is already a node at that position then retreave it
                newNode = self.graph.findNodeByPos(current_pos)
            else:
                newNode = self.graph.nodes[-1]

            ##then create an edge between the this node and the focus node
            if not self.graph.focus_node.addEdge(newNode):
                ##if the edge exists then return
                return

            else:
                self.graph.setFocusByPos(current_pos)

        ##if some nodes have recently been undone and you are creating new nodes
        if self.graph.undone_nodes:
            ##officially delete the undone nodes
            del self.graph.undone_nodes[:]

        #because state has likely changes we ReDraw
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll()

    def OnMove(self, event):
        if self.firstClick:
            newPos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
            coords = (self.graph.focus_node.pos , newPos)
            # self.Canvas.AddSmoothArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
            self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
            #we draw the graoh here because the state has most probably changed
            self.graph.draw(self.Canvas)
            self.Canvas.Draw()
            self.Canvas.ClearAll()


"""
SELECTION
    THIS GUIMODE IS FOR SELECTING NODES ON A GRAPH AND MOVING THEM.
    LATER DELETION AND OTHER FORMS OF EDITING WILL BE SUPPORTED
"""
class GUISelectNode(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph
        self.selected_node = None

    def OnLeftDown(self, event):
        #get the snap position of the selection
        pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
        #get the node selected if infact a node was selected
        #if there is no node at the click posistion then the
        #self.selected_node will still be none
        #and the condition in OnMove will not be satisfied
        self.selected_node = self.graph.focus_node = self.graph.findNodeByPos(pos)


    def OnMove(self, event):
        if self.selected_node and event.Dragging():
            pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
            ##look for a node at the new position in the graph
            ##if you get something back then you know
            ##that you can't put the node there
            other_node = self.graph.findNodeByPos(pos)
            if not other_node:
                self.graph.focus_node.pos = pos

            self.graph.draw(self.Canvas)
            self.Canvas.Draw()
            self.Canvas.ClearAll()

    def OnLeftUp(self, event):
        #stop selection
        #self.selected_node = None
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll()


class GUISelectEdge(GUIMode.GUIMouse):
    def __init__(self, canvas = None, graph = None):
        self.Canvas = canvas
        self.graph = graph
        self.selected_edge = None


    def OnLeftDown(self, event):
        pos = self.Canvas.PixelToWorld(event.GetPosition())
        self.selected_edge = self.graph.getEdgeFromPoint(pos, margin=5)
        if self.selected_edge:
            self.graph.focus_edge = self.selected_edge
            self.graph.draw(self.Canvas)
            self.Canvas.Draw()
            self.Canvas.ClearAll()

###############################################################################
##UI GRAPH#####################################################################
###############################################################################


class GraphDesignPanel(wx.Panel):
    def __init__(self, parent, graph=None):
        wx.Panel.__init__(self, parent)

        self.graph = graph

        self.SetBackgroundColour('WHITE')
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Canvas = FloatCanvas.FloatCanvas(self)

        # InitAll() sets everything in the Canvas to default state.
        # It can be used to reset the Canvas
        self.Canvas.InitAll()
        self.Canvas.GridUnder = FloatCanvas.DotGrid((grid_cell_size, grid_cell_size), Size=3, Color="BLACK")

        self.Modes = {
                      "AddNodes": GUIAddNodes(self.Canvas, self.graph),
                      "ZoomIn" :  GUIMode.GUIZoomIn(),
                      "ZoomOut": GUIMode.GUIZoomOut(),
                      "Pan" :  GUIMode.GUIMove(),
                      "SelectNodes" : GUISelectNode(self.Canvas, self.graph),
                      "SelectEdges" : GUISelectEdge(self.Canvas, self.graph)
                     }

        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.Canvas, 1, wx.GROW)

        self.SetSizerAndFit(box_sizer)

        self.Canvas.SetMode(self.Modes["AddNodes"])

    def SetMode(self, arg_mode):
        self.Canvas.SetMode(self.Modes[arg_mode])
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll()
        self.graph.draw(self.Canvas)
