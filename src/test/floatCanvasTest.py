# CreateRadialGradientBrush (self, xo, yo, xc, yc, radius, oColor, cColor)
# Canvas.AddCircle(xy, D, LineWidth = lw, LineColor = colors[cl], FillColor = colors[cf])
# Canvas.AddText("Circle # %i"%(i), xy, Size = 12, BackgroundColor = None, Position = "cc")

import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

SCREEN_HEIGHT = 640
SCREEN_WIDTH = 800
grid_cell_size = 30
#
def YDownProjection(CenterPoint):
    return N.array((1, -1))

class SmoothArrowLine(FloatCanvas.PointsObjectMixin, FloatCanvas.LineOnlyMixin, FloatCanvas.DrawObject):
    """
    ArrowLine class definition.

    API definition::

        ArrowLine(Points, # coords of points
                  LineColor = "Black",
                  LineStyle = "Solid",
                  LineWidth    = 1,
                  ArrowHeadSize = 4, # in pixels
                  ArrowHeadAngle = 45,
                  InForeground = False):


    It will draw a set of arrows from point to point.

    It takes a list of 2-tuples, or a NX2 NumPy Float array
    of point coordinates.


    """

    def __init__(self,
                 Points,
                 LineColor = "Black",
                 LineStyle = "Solid",
                 LineWidth    = 1, # pixels
                 ArrowHeadSize = 8, # pixels
                 ArrowHeadAngle = 30, # degrees
                 InForeground = False):

        FloatCanvas.DrawObject.__init__(self, InForeground)

        self.Points = N.asarray(Points,N.float)
        self.Points.shape = (-1,2) # Make sure it is a NX2 array, even if there is only one point
        self.ArrowHeadSize = ArrowHeadSize
        self.ArrowHeadAngle = float(ArrowHeadAngle)

        self.CalcArrowPoints()
        self.CalcBoundingBox()

        self.LineColor = LineColor
        self.LineStyle = LineStyle
        self.LineWidth = LineWidth

        self.SetPen(LineColor,LineStyle,LineWidth)

        self.HitLineWidth = max(LineWidth,self.MinHitLineWidth)

    def CalcArrowPoints(self):
        S = self.ArrowHeadSize
        phi = self.ArrowHeadAngle * N.pi / 360
        Points = self.Points
        n = Points.shape[0]
        self.ArrowPoints = N.zeros((n-1, 3, 2), N.float)
        for i in xrange(n-1):
            dx, dy = self.Points[i] - self.Points[i+1]
            theta = N.arctan2(dy, dx)
            AP = N.array( (
                            (N.cos(theta - phi), -N.sin(theta-phi)),
                            (0,0),
                            (N.cos(theta + phi), -N.sin(theta + phi))
                            ),
                          N.float )
            self.ArrowPoints[i,:,:] = AP
        self.ArrowPoints *= S

    def _Draw(self, dc , WorldToPixel, ScaleWorldToPixel, HTdc=None):
        Points = WorldToPixel(self.Points)
        ArrowPoints = Points[1:,N.newaxis,:] + self.ArrowPoints
        dc.SetPen(self.Pen)
        dc.DrawLines(Points)
        GC = wx.GraphicsContext.Create(dc)
        GC.SetPen(self.Pen)
        GC.DrawLines(Points)
        for arrow in ArrowPoints:
                GC.DrawLines(arrow)


class Example(wx.Frame):
    def __init__(self, parent, id, title, position, size):
        wx.Frame.__init__(self, parent, id, title, position, size)
        self.InitUI()
        ##BIND MOUSE EVENTS
        self.Canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onLeftDown)
        self.Canvas.Bind(FloatCanvas.EVT_MOTION, self.onMouseMove)
        self.Canvas.Bind(FloatCanvas.EVT_MOUSEWHEEL, self.onWheel)
        ##BIND KEYBOARD EVENTS
        self.Canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        ##CHANGE TO INITIALIZE WITH TOOLBAR BUTTON
        self.firstClick = False
        self.lines = []
        self.node_pos_list = []
        self.redo_lines = []
        self.redo_nodes = []


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
                             ProjectionFun=YDownProjection,
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
        if self.firstClick is False:
            self.firstClick = True
            self.pos = self.getSnapPos(event.GetCoords())
            self.Canvas.AddCircle(self.pos, 10, LineWidth=1, LineColor='BLACK', FillColor='BLACK')
            self.node_pos_list.append(self.pos)
            print self.pos
        else:
            self.lines.append((self.pos, self.getSnapPos(event.GetCoords())))
            if len(self.lines) != 0:
                self.pos = self.getSnapPos(event.GetCoords())
                print self.pos
                self.node_pos_list.append(self.pos)
        event.Skip()

    def onKeyDown(self, event):

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
           self.firstClick = False
           print self.lines
           print self.node_pos_list
        #elif key_code == wx.WXK_TAB:



    ##POSSIBLY DEPRECIATED
    def getSnapPos(self, arg_pos):
        return (grid_cell_size* round(arg_pos[0]/grid_cell_size), grid_cell_size*round(arg_pos[1]/grid_cell_size))

    def onMouseMove(self,event):
        if event.Moving() and self.firstClick:
            self.drawMotion(event)
        event.Skip()


    def drawMotion(self, event):
        self.newPos = self.getSnapPos(event.GetCoords())
        coords = (self.pos , self.newPos)
        print coords
        arrowline = FloatCanvas.SmoothArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
        self.Canvas.AddObject(arrowline)
        #self.Canvas.AddSmoothArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
        self.Canvas.Draw()
        self.Canvas.InitAll()
        for line in self.lines:
            le_arrowline = FloatCanvas.SmoothArrowLine(line, LineWidth=2, LineColor='BLUE', ArrowHeadSize=16)
            self.Canvas.AddObject(le_arrowline)
            #self.Canvas.AddSmoothArrowLine(line, LineWidth=2, LineColor="RED", ArrowHeadSize=16)
        for nodes in self.node_pos_list:
            self.Canvas.AddCircle(nodes, 10, LineWidth=1, LineColor='BLACK', FillColor='BLACK')

    def onWheel(self, event):
        pass

def main():

    ex = wx.App()
    Example(None, wx.ID_ANY, "TEST", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
