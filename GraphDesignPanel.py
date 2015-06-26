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
import PypeGraph as PG
import Geometry as Geom

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

        if not self.graph.addNode(current_pos):
            self.graph.setFocusByPos(current_pos)

        self.graph.setFocusByPos(current_pos)


        ##if some nodes have recently been undone and you are creating new nodes
        if self.graph.undone_nodes:
            ##officially delete the undone nodes
            del self.graph.undone_nodes[:]

        #because state has likely changes we ReDraw
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)


"""
ADD PIPES
    THIS GUI MODE IS FOR ADDING PIPES BETWEEN NODES
"""

class GUIAddPipes(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph
        self.firstNode = None
        self.secondNode = None

    def OnLeftDown(self, event):

        ##get the position of the click
        current_pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
        ##if this is the first click
        if not self.firstNode:
            ##if there is already an node at the position in the graph
            self.firstNode = self.graph.findNodeByPos(current_pos)

        ##otherwise it's the second click
        else:
            ##first add a node to the graph
            self.secondNode = self.graph.findNodeByPos(current_pos)

        ##if some nodes have recently been undone and you are creating new nodes
        if self.graph.undone_nodes:
            ##officially delete the undone nodes
            del self.graph.undone_nodes[:]

        #because state has likely changes we ReDraw
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)

    def OnLeftUp(self, event):
        if self.firstNode and self.secondNode and (self.firstNode is not self.secondNode):
            if self.firstNode.addEdge(self.secondNode):
                self.firstNode = self.secondNode = None
            else:
                print "cannot add edge"
                self.secondNode = None
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)


    def OnMove(self, event):
        if self.firstNode:
            newPos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
            coords = (self.firstNode.pos , newPos)
            self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
            #we draw the graoh here because the state has most probably changed
            self.graph.draw(self.Canvas)
            self.Canvas.Draw()
            self.Canvas.ClearAll(ResetBB=False)

"""
ADD NON-PIPE ELEMENTS
    THIS GUI MODE WILL ADD NON-PIPE ELEMENTS TO THE PIPES
"""
class GUIAddNonPipeElement(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph



"""
SELECTION
    THIS GUIMODE IS FOR SELECTING NODES ON A GRAPH AND MOVING THEM.
    LATER DELETION AND OTHER FORMS OF EDITING WILL BE SUPPORTED
"""
class GUISelect(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph
        self.selection = None

    def OnLeftDown(self, event):
        #get the snap position of the selection
        snap_pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
        real_pos = self.Canvas.PixelToWorld(event.GetPosition())
        #get the node selected if infact a node was selected
        #if there is no node at the click posistion then the
        #self.selected_node will still be none
        #and the condition in OnMove will not be satisfied
        node = self.graph.findNodeByPos(snap_pos)
        edge = self.graph.getEdgeFromPoint(real_pos, margin = 4)

        if edge:
            self.selection = self.graph.focus_edge = edge
            self.graph.focus_node = None
        elif node:
            self.selection = self.graph.focus_node = node
            self.graph.focus_edge = None


        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)

    # def OnMove(self, event):
    #     if self.graph.focus_node and event.Dragging():
    #         pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
    #         ##look for a node at the new position in the graph
    #         ##if you get something back then you know
    #         ##that you can't put the node there
    #         other_node = self.graph.findNodeByPos(pos)
    #         if not other_node:
    #             self.graph.focus_node.pos = pos
    #
    #         self.graph.draw(self.Canvas)
    #         self.Canvas.Draw()
    #         self.Canvas.ClearAll(ResetBB=False)

    def OnLeftUp(self, event):
        #stop selection
        #self.selected_node = None
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)


class GUIMove(GUIMode.GUIMouse):
    def __init__(self, canvas = None, graph = None):
        self.Canvas = canvas
        self.graph = graph
        self.allow_move = False
        self.premove_pos = None
        self.decision = None

    def OnLeftDown(self, event):

        focus = self.graph.focus_node
        if focus:
            pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
            if pos == focus.pos:
                self.allow_move = True
                self.premove_pos = self.graph.focus_node.pos


    def OnMove(self, event):
        if self.graph.focus_node and event.Dragging() and self.allow_move:


            pos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))

            ##look for a node at the new position in the graph
            ##if you get something back then you know
            ##that you can't put the node there
            other_node = self.graph.findNodeByPos(pos)
            if not other_node:
                self.graph.focus_node.pos = pos

            #we draw the graoh here because the state has most probably changed
            self.graph.draw(self.Canvas)
            self.Canvas.Draw()
            self.Canvas.ClearAll(ResetBB=False)


    def OnLeftUp(self, event):
        if self.allow_move:
            ## We want the message to be current to the present focus so the message must be reset here.
            self.message = "Moving node " + str(self.graph.focus_node.label)
            self.message += " will delete all the non-pipe elements on pipes "
            self.message += "connected to it. Are you sure you want to move this node?"
            self.message += " Press 'Ok' to continue moving it"

            if self.graph.focus_node.pos != self.premove_pos:
                self.decision = wx.MessageBox(self.message, "Move Warning!", wx.OK | wx.CANCEL )
                ## if the decision is ok then make the change
                if self.decision == wx.OK:

                    for node in self.graph.nodes:
                        for edge in node._neighbors:
                            if edge.node == self.graph.focus_node:
                                del edge.elements [:]

                    for edge in self.graph.focus_node._neighbors:
                        del edge.elements[:]

            if self.decision == wx.CANCEL:
                self.graph.focus_node.pos = self.premove_pos


        self.allow_move = False
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)


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
        self.Modes = {
                      "AddNodes": GUIAddNodes(self.Canvas, self.graph),
                      "AddPipes": GUIAddPipes(self.Canvas, self.graph),
                      "ZoomIn" :  GUIMode.GUIZoomIn(),
                      "ZoomOut": GUIMode.GUIZoomOut(),
                      "Pan" :  GUIMode.GUIMove(),
                      "Select" : GUISelect(self.Canvas, self.graph),
                      "Move" : GUIMove(self.Canvas, self.graph)
                     }


        # self.BuildToolbar()

        ## Create the vertical sizer for the toolbar and Panel
        # Remember that verticial means the widgets will stack vertically
        # You need to have a sizer for all widgets in the GUI
        # In general the hierarchy needs to be followed container --> widget
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        # box_sizer.Add(self.ToolBar, 0, wx.ALL | wx.ALIGN_LEFT | wx.GROW, 4)

        # second parameter refers to "proportionality" so the toolbar to drawing area will be 1:6
        box_sizer.Add(self.Canvas, 1, wx.GROW)

        # Top most sizer has to be set
        self.SetSizerAndFit(box_sizer)

        self.Canvas.SetMode(GUIMode.GUIMouse())



    # REMOVE LATER, MOVE FUNCTIONALITY TO RIBBON TOOLBAR

    # def BuildToolbar(self):
    #     """
    #     This is here so it can be over-ridden in a ssubclass, to add extra tools, etc
    #     """
    #     tb = wx.ToolBar(self)
    #     self.ToolBar = tb
    #
    #     tb.SetToolBitmapSize((24, 24))
    #     self.AddToolbarModeButtons(tb, self.Modes)
    #
    #     tb.Realize()

    # def AddToolbarModeButtons(self, tb, Modes):
    #     self.ModesDict = {}
    #     for Mode in Modes:
    #         tool = tb.AddRadioTool(wx.ID_ANY, shortHelp=Mode[0], bitmap=Mode[2])
    #         self.Bind(wx.EVT_TOOL, self.SetMode, tool)
    #         self.ModesDict[tool.GetId()]=Mode[1]
    #     #self.ZoomOutTool = tb.AddRadioTool(wx.ID_ANY, bitmap=Resources.getMagMinusBitmap(), shortHelp = "Zoom Out")
    #     #self.Bind(wx.EVT_TOOL, lambda evt : self.SetMode(Mode=self.GUIZoomOut), self.ZoomOutTool)
    #
    #
    #
    # def HideShowHack(self):
    #     ##fixme: remove this when the bug is fixed!
    #     """
    #     Hack to hide and show button on toolbar to get around OS-X bug on
    #     wxPython2.8 on OS-X
    #     """
    #     self.ZoomButton.Hide()
    #     self.ZoomButton.Show()

    ## takes a string argument that is a key to the modes
    ## dictionary
    def SetMode(self, arg_mode):
        self.Canvas.SetMode(self.Modes[arg_mode])
        self.graph.draw(self.Canvas)
        self.Canvas.Draw()
        self.Canvas.ClearAll(ResetBB=False)
        self.graph.draw(self.Canvas)
