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

        # This is all from Navcanvas, to keep funtionality, I'll take these calls to FloatCanvas.GUIMode and bind them
        # to the actual GUI Toolbar, later...
        self.Modes = [
                      ("Add Nodes", GUIAddNodes(self.Canvas, self.graph), Resources.getPointerBitmap()),
                      ("Zoom In",  GUIMode.GUIZoomIn(),  Resources.getMagPlusBitmap()),
                      ("Zoom Out", GUIMode.GUIZoomOut(), Resources.getMagMinusBitmap()),
                      ("Pan",      GUIMode.GUIMove(),    Resources.getHandBitmap()),
                      ("Select Nodes", GUISelectNode(self.Canvas, self.graph), Resources.getHandBitmap()),
                      ("Select Edges", GUISelectEdge(self.Canvas, self.graph), Resources.getHandBitmap()),
                     ]


        self.BuildToolbar()

        ## Create the vertical sizer for the toolbar and Panel
        # Remember that verticial means the widgets will stack vertically
        # You need to have a sizer for all widgets in the GUI
        # In general the hierarchy needs to be followed container --> widget
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.ToolBar, 0, wx.ALL | wx.ALIGN_LEFT | wx.GROW, 4)

        # second parameter refers to "proportionality" so the toolbar to drawing area will be 1:6
        box_sizer.Add(self.Canvas, 1, wx.GROW)

        # Top most sizer has to be set
        self.SetSizerAndFit(box_sizer)

        self.Canvas.SetMode(self.Modes[0][1])

    # REMOVE LATER, MOVE FUNCTIONALITY TO RIBBON TOOLBAR

    def BuildToolbar(self):
        """
        This is here so it can be over-ridden in a ssubclass, to add extra tools, etc
        """
        tb = wx.ToolBar(self)
        self.ToolBar = tb

        tb.SetToolBitmapSize((24, 24))
        self.AddToolbarModeButtons(tb, self.Modes)

        tb.Realize()

    def AddToolbarModeButtons(self, tb, Modes):
        self.ModesDict = {}
        for Mode in Modes:
            tool = tb.AddRadioTool(wx.ID_ANY, shortHelp=Mode[0], bitmap=Mode[2])
            self.Bind(wx.EVT_TOOL, self.SetMode, tool)
            self.ModesDict[tool.GetId()]=Mode[1]
        #self.ZoomOutTool = tb.AddRadioTool(wx.ID_ANY, bitmap=Resources.getMagMinusBitmap(), shortHelp = "Zoom Out")
        #self.Bind(wx.EVT_TOOL, lambda evt : self.SetMode(Mode=self.GUIZoomOut), self.ZoomOutTool)



    def HideShowHack(self):
        ##fixme: remove this when the bug is fixed!
        """
        Hack to hide and show button on toolbar to get around OS-X bug on
        wxPython2.8 on OS-X
        """
        self.ZoomButton.Hide()
        self.ZoomButton.Show()

    def SetMode(self, event):
        Mode = self.ModesDict[event.GetId()]
        self.Canvas.SetMode(Mode)
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll()
        self.graph.draw(self.Canvas)
