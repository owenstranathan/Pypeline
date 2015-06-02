# CreateRadialGradientBrush (self, xo, yo, xc, yc, radius, oColor, cColor)
# Canvas.AddCircle(xy, D, LineWidth = lw, LineColor = colors[cl], FillColor = colors[cf])
# Canvas.AddText("Circle # %i"%(i), xy, Size = 12, BackgroundColor = None, Position = "cc")

import wx
import numpy as N
import PypeGraph as PypeGraph
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

SCREEN_HEIGHT = 640
SCREEN_WIDTH = 800
grid_cell_size = 30




class OpacityMixin:
    def SetBrush(self, FillColor, FillStyle):
        "Like standard SetBrush except that FillStyle is an integer giving\
        opacity , where 0<=opacity<=255"

        opacity = FillStyle

        c = wx.Color()
        c.SetFromName(FillColor)
        r,g,b = c.Get()
        c = wx.Color(r,g,b,opacity)
        self.Brush = wx.Brush(c)


class AlphaCircle(OpacityMixin, FloatCanvas.Circle):
    def __init__(self, XY, Diameter, **kwargs):
        FloatCanvas.Circle.__init__(self, XY, Diameter, **kwargs)
        self.XY = self.Center

    def _Draw(self, dc, WorldToPixel, ScaleWorldToPixel, HTdc=None):
        gc = wx.GraphicsContext.Create(dc)
        (XY, WH) = self.SetUpDraw(gc, WorldToPixel, ScaleWorldToPixel, HTdc)

        path = gc.CreatePath()
        center = XY
        radius = WH[0] * 0.5

        path.AddCircle(center[0], center[1], radius)

        gc.PushState()
        gc.SetPen(wx.Pen(self.LineColor, self.LineWidth))
        gc.SetBrush(self.Brush)
        gc.DrawPath(path)
        gc.PopState()



class Example(wx.Frame):
    def __init__(self, parent, id, title, position, size):
        wx.Frame.__init__(self, parent, id, title, position, size)
        self.graph = PypeGraph.DrawingGraph()
        self.InitUI()
        ##BIND MOUSE EVENTS
        self.Canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onLeftDown)
        self.Canvas.Bind(FloatCanvas.EVT_MOTION, self.onMouseMove)
        self.Canvas.Bind(FloatCanvas.EVT_MOUSEWHEEL, self.onWheel)
        ##BIND KEYBOARD EVENTS
        self.Canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        ## BIND CHAR EVENT
        self.Canvas.Bind(wx.EVT_CHAR, self.onCharEvent)
        ##BIND IDLE EVENT
        #self.Canvas.Bind(wx.EVT_IDLE, self.draw)

        ##CHANGE TO INITIALIZE WITH TOOLBAR BUTTON
        self.firstClick = False

        ##undo history so that you can redo
        self.undone_nodes = []


    ##INIT UI AND FRAME_SETTINGS
    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Canvas = NavCanvas.NavCanvas(self, -1,
                             size=(500, 500),
                             ProjectionFun=None,
                             Debug=0,
                             BackgroundColor="White",
                             ).Canvas

        # InitAll() sets everything in the Canvas to default state.
        # It can be used to reset the Canvas
        self.Canvas.InitAll()

        self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.SetTitle('ASRAD Ueber Alles')
        self.Canvas.ZoomToBB()
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

    ##LEFT CLICK EVENT HANDLER
    def onLeftDown(self, event):
        #for node in self.graph.nodes:
        #    print node.label, " : " , node._neighbors
        #get the position of the click
        current_pos = self.getSnapPos(event.GetCoords())
        #if this is the first click
        if self.firstClick is False:
            self.firstClick = True
            ##if there is already an node at the position in the graph
            if not self.graph.addNode(current_pos):
                self.graph.setFocus(current_pos)

            self.graph.setFocus(current_pos)


        #otherwise it's the second click
        else:
            #first add a node to the graph
            if not self.graph.addNode(current_pos):
                #if there is already a node at that position then retreave it
                newNode = self.graph.findNode(current_pos)
            else:
                newNode = self.graph.nodes[-1]

            #then create an edge between the this node and the focus node
            if not self.graph.focus_node.addEdge(newNode):
                ##if the edge exists then return
                print "CANNOT ADD DUPLICATE EDGE"
                event.Skip()
                return

            else:
                self.graph.setFocus(current_pos)

        ##if some nodes have recently been undone and you are creating new nodes
        if self.undone_nodes:
            ##officially delete the undone nodes
            del self.undone_nodes[:]

        self.pos = current_pos

        event.Skip()

    def onKeyDown(self, event):

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
           self.firstClick = False
           self.Canvas.InitAll
           self.graph.draw(self.Canvas)
           self.Canvas.Draw()
        event.Skip()

        #elif key_code == wx.WXK_TAB:

    ##undoes nodes
    def undo(self, coords):
        ##if the graph is empty do nothing
        if not self.graph.nodes:
            print "nothing to undo"
            return
        ##other wise
        else:
            ##push the last node added to the graph onto the
            ##undo history stack
            ##I say stack because that's really what it is
            ##it's a list that practices last in first out
            ##i.e. a stack
            self.undone_nodes.append(self.graph.pop())
            self.graph.resetFocus()
            self.pos = self.graph.focus_node.pos


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
            if not self.graph.addNodeDirectly(zombieNode):
                print "cannot add node"
                return
            ##if you can add it
            else:
                ##try and make the edge
                ##this might have a fail condition but##not one that I can think
                ##of, maybe you're smarter than me ;)
                if not self.graph.focus_node.addEdge(zombieNode):
                    print "cannot add edge"
                    return
                ##if that's successfull(it should be)
                ##then reset the focus
                ##and the current pos
                else:
                    print self.graph.focus_node
                    self.graph.resetFocus
                    self.pos = zombieNode.pos


    def onCharEvent(self,event):

        ctrlDown = event.CmdDown()
        keyCode = event.GetKeyCode()
        if ctrlDown and keyCode is 89:
            self.redo(self.getSnapPos(event.GetPosition()))
        elif ctrlDown and keyCode is 90:
            self.undo(self.getSnapPos(event.GetPosition()))
        event.Skip()
        ##other stuff


    def getSnapPos(self, arg_pos):
        return (
            grid_cell_size* round(arg_pos[0]/grid_cell_size),
            grid_cell_size*round(arg_pos[1]/grid_cell_size)
            )

    def onMouseMove(self,event):
        if event.Moving() and self.firstClick:
            self.drawMotion(event)
        event.Skip()


    def drawMotion(self, event):
        self.newPos = self.getSnapPos(event.GetCoords())
        coords = (self.pos , self.newPos)
        self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)

        #we draw the graoh here because the state has most probably changed
        self.draw()

        event.Skip()

    def draw(self):
        self.Canvas.Draw()
        self.Canvas.ClearAll()
        self.graph.draw(self.Canvas)

    def onWheel(self, event):
        pass

def main():

    ex = wx.App()
    Example(None, wx.ID_ANY, "TEST", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
