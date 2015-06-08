'''
        This is PypeGraph.py
        PypeGraph uses the Graph structure defined in Pypeline.py
        an wxPython/FloatCanvas to create a drawing
        surface for creating a pipeline network model

        further more it defines drawing utilities for
        graphically representing a graph

        ##contracts
'''
import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, GUIMode, Resources


##Can't use Python Enumerations in Python2.7 which is what wx uses
##so we have to use a Hack
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

##enumeration for different input modes
modes = enum('Select', 'Design')

##EDIT
##We are going to use the floatcanvas way of making GUIModes to switch
##between different ways of handling input(events)
##this is actually good OOP design because we are encapsulating
##behaviors within the larger Deign panel class

'''
    GUI Modes for DesignPanel
'''

class GUIDesign(GUIMode.GUIBase):
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
                self.graph.setFocus(current_pos)

            self.graph.setFocus(current_pos)

        ##otherwise it's the second click
        else:
            ##first add a node to the graph
            if not self.graph.addNode(current_pos):
                ##if there is already a node at that position then retreave it
                newNode = self.graph.findNode(current_pos)
            else:
                newNode = self.graph.nodes[-1]

            ##then create an edge between the this node and the focus node
            if not self.graph.focus_node.addEdge(newNode):
                ##if the edge exists then return
                print "CANNOT ADD DUPLICATE EDGE"
                return

            else:
                self.graph.setFocus(current_pos)

        ##if some nodes have recently been undone and you are creating new nodes
        if self.graph.undone_nodes:
            ##officially delete the undone nodes
            del self.graph.undone_nodes[:]

        #because state has likely changes we ReDraw
        self.Canvas.Draw()
        self.Canvas.ClearAll()
        self.graph.draw(self.Canvas)

    def OnMove(self, event):
        if self.firstClick:
            newPos = getSnapPos(self.Canvas.PixelToWorld(event.GetPosition()))
            coords = (self.graph.focus_node.pos , newPos)
            self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
            #we draw the graoh here because the state has most probably changed
            self.Canvas.Draw()
            self.Canvas.ClearAll()
            self.graph.draw(self.Canvas)

######################
##Unfinished!!!!!!!
##Selection will be handled in the selection GUImode
##which is this
'''Selection'''
class GUISelect(GUIMode.GUIBase):
    def __init__(self, canvas=None, graph=None):
        GUIMode.GUIBase.__init__(self, canvas)
        self.graph = graph


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


class GraphDesignPanel(wx.Panel):
    def __init__(self, parent, graph=None):
        wx.Panel.__init__(self, parent)

        self.graph = graph

        self.SetBackgroundColour('WHITE')
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Canvas = FloatCanvas.FloatCanvas(self)

        ##default start the design panel is select mode
        self.mode = modes.Design

        ##CHANGE TO INITIALIZE WITH TOOLBAR BUTTON
        ##self.firstClick = False

        # ##BIND MOUSE EVENTS
        # self.Canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onLeftDown)
        # self.Canvas.Bind(FloatCanvas.EVT_MOTION, self.onMouseMove)
        # ##BIND KEYBOARD EVENTS
        # self.Canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # ## BIND CHAR EVENT
        # self.Canvas.Bind(wx.EVT_CHAR, self.onCharEvent)

        # InitAll() sets everything in the Canvas to default state.
        # It can be used to reset the Canvas
        self.Canvas.InitAll()
        self.Canvas.GridUnder = FloatCanvas.DotGrid((30,30), Size=3, Color="BLACK")

        # This is all from Navcanvas, to keep funtionality, I'll take these calls to FloatCanvas.GUIMode and bind them
        # to the actual GUI Toolbar, later...
        self.Modes = [("Pointer",  GUIMode.GUIMouse(),   Resources.getPointerBitmap()),
                      ("Zoom In",  GUIMode.GUIZoomIn(),  Resources.getMagPlusBitmap()),
                      ("Zoom Out", GUIMode.GUIZoomOut(), Resources.getMagMinusBitmap()),
                      ("Pan", GUIMode.GUIMove(),    Resources.getHandBitmap()),
                      ("Design", GUIDesign(self.Canvas, self.graph), Resources.getPointerBitmap()),
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
        self.AddToolbarZoomButton(tb)
        tb.Realize()

    def AddToolbarModeButtons(self, tb, Modes):
        self.ModesDict = {}
        for Mode in Modes:
            tool = tb.AddRadioTool(wx.ID_ANY, shortHelp=Mode[0], bitmap=Mode[2])
            self.Bind(wx.EVT_TOOL, self.SetMode, tool)
            self.ModesDict[tool.GetId()]=Mode[1]
        #self.ZoomOutTool = tb.AddRadioTool(wx.ID_ANY, bitmap=Resources.getMagMinusBitmap(), shortHelp = "Zoom Out")
        #self.Bind(wx.EVT_TOOL, lambda evt : self.SetMode(Mode=self.GUIZoomOut), self.ZoomOutTool)

    def AddToolbarZoomButton(self, tb):
        tb.AddSeparator()

        self.ZoomButton = wx.Button(tb, label="Zoom To Fit")
        tb.AddControl(self.ZoomButton)
        self.ZoomButton.Bind(wx.EVT_BUTTON, self.ZoomToFit)


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

    def ZoomToFit(self,Event):
        self.Canvas.ZoomToBB()
        self.Canvas.SetFocus() # Otherwise the focus stays on the Button, and wheel events are lost.


    ##LEFT CLICK EVENT HANDLER
    # def onLeftDown(self, event):
    #     ##skip the event
    #     event.Skip()
    #     if self.mode is modes.Design:
    #         self.designMode(event)
    #     elif self.mode is modes.Select:
    #         self.selectMode(event)
    #
    # def selectMode(self, event):
    #     pass
    #
    # def designMode(self, event):
    #     ##get the position of the click
    #     current_pos = getSnapPos(event.GetCoords())
    #     ##if this is the first click
    #     if self.firstClick is False:
    #         self.firstClick = True
    #         ##if there is already an node at the position in the graph
    #         if not self.graph.addNode(current_pos):
    #             self.graph.setFocus(current_pos)
    #
    #         self.graph.setFocus(current_pos)
    #
    #     ##otherwise it's the second click
    #     else:
    #         ##first add a node to the graph
    #         if not self.graph.addNode(current_pos):
    #             ##if there is already a node at that position then retreave it
    #             newNode = self.graph.findNode(current_pos)
    #         else:
    #             newNode = self.graph.nodes[-1]
    #
    #         ##then create an edge between the this node and the focus node
    #         if not self.graph.focus_node.addEdge(newNode):
    #             ##if the edge exists then return
    #             print "CANNOT ADD DUPLICATE EDGE"
    #             return
    #
    #         else:
    #             self.graph.setFocus(current_pos)
    #
    #     ##if some nodes have recently been undone and you are creating new nodes
    #     if self.graph.undone_nodes:
    #         ##officially delete the undone nodes
    #         del self.graph.undone_nodes[:]
    #
    #     #because state has likely changes we ReDraw
    #     self.draw

    ##Handle Character Events
    # def onCharEvent(self,event):
    #     event.Skip()
    #     ctrlDown = event.CmdDown()
    #     keyCode = event.GetKeyCode()
    #     ##is ctrl and 'Y' pressed
    #     if ctrlDown and keyCode is 89:
    #         self.graph.redo()
    #         self.draw()
    #     ##is ctrl and 'Z' presed
    #     elif ctrlDown and keyCode is 90:
    #         self.graph.undo()
    #         self.draw()
    #     #because state has likely changes we ReDraw
    #     self.draw
    #     ##other stuff
    #
    # def onMouseMove(self, event):
    #     event.Skip()
    #     if self.firstClick:
    #         self.drawMotion(event)
    #
    #     ##other stuff
    #
    #
    # def onKeyDown(self, event):
    #     key_code = event.GetKeyCode()
    #     if key_code == wx.WXK_ESCAPE:
    #        self.firstClick = False
    #        ##because of state change we draw
    #        #self.draw()
    #     event.Skip()
    #
    # ##to draw mouse movement between clicks
    # def drawMotion(self, event):
    #     self.newPos = getSnapPos(event.GetCoords())
    #     coords = (self.graph.focus_node.pos , self.newPos)
    #     self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
    #     #we draw the graoh here because the state has most probably changed
    #     self.draw()
    #
    # ##this uses BFT(breadth first traversal) to draw every node and
    # ##edge in the graph
    # def drawGraph(self):
    #     for node in self.graph.nodes:
    #         self.Canvas.AddCircle(
    #             node.pos,
    #             10,
    #             LineWidth=1,
    #             LineColor='BLACK',
    #             FillColor='BLACK'
    #         )
    #         for edge in node._neighbors:
    #             line = (node.pos, edge.node.pos)
    #             self.Canvas.AddArrowLine(
    #                 line, LineWidth=2,
    #                 LineColor="RED",
    #                 ArrowHeadSize=16
    #             )
    #
    #
    # def draw(self):
    #     self.Canvas.Draw()
    #     self.Canvas.ClearAll()
    #     self.graph.drawGraph()
