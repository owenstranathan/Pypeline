
import wx


class DrawingGridWindow(wx.Window):


    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        self.SetBackgroundColour("White")
        self.color = "Black"
        self.thickness = 1
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)
        self.zoom = 1
        # self.InitBuffer()
        #self.pos = (0,0)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
        #FOR DRAWING############################################################

        self.lines = []
        self.firstClick = False
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)


        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.size_initial = parent.GetSize()
        self.width, self.height = self.size_initial
        # scale size of cell
        self.scale = 16
        self.SetDoubleBuffered(True)
        self.InitBuffer()

    def OnErase(self, event):
        # Cody Precord
        # Do nothing, reduces flicker by removing
        # unneeded background erasures and redraws
        pass


    #DRAWING RELATED FUNCTIONS##################################################
    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.drawGrid(dc)
        self.reInitBuffer = False


    '''Find the snap position relative to the grid size'''
    def getSnapPos(self, arg_pos):
        return (self.scale* round(arg_pos[0]/self.scale), self.scale*round(arg_pos[1]/self.scale))

    '''Draws lines when left mouse button is clicked'''
    def OnLeftDown(self, event):
        #print event.GetEventType()
        if self.firstClick is False:
            self.firstClick = True
            self.pos = self.getSnapPos(event.GetPositionTuple())
        else:
            self.lines.append(self.pos + self.getSnapPos(event.GetPositionTuple()))
            if len(self.lines) != 0:
               self.pos = self.getSnapPos(event.GetPositionTuple())

        event.Skip()


    def keyDown(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
           self.firstClick = False

    def OnMotion(self, event):
        eventType = event.GetEventType()
        if eventType == wx.EVT_MOTION:
            print "true true"
        if event.Moving() and self.firstClick:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            self.drawMotion(dc, event)
            event.Skip()

    def drawMotion(self, dc, event):

        dc.Clear()
        dc.SetPen(wx.Pen("RED", 3, wx.SOLID))
        self.newPos = self.getSnapPos(event.GetPositionTuple())
        coords = self.pos + self.newPos
        dc.DrawLine(*coords)
        self.DrawLines(dc)
        self.drawGrid(dc)

    def DrawLines(self, dc):
        dc.SetPen(wx.Pen("GREEN", 3, wx.SOLID))
        for line in self.lines:
            dc.DrawLine(*line)


    def onScroll(self, event):

        sign = event.GetWheelRotation() / 120
        if(sign > 0):
            self.zoom = self.zoom * 1.05
            self.Refresh()
        else:
            self.zoom = self.zoom * 0.95
            self.Refresh()

    def OnSize(self, event):
        self.InitBuffer()
        size = self.GetClientSize()
        self.width, self.height = size


    def drawGrid(self, dc):
        dc.SetPen(self.pen)
        for i in range(0, self.width/self.scale):
            dc.DrawLine(i*self.scale,0, i*self.scale, self.height)
        for i in range(0, self.height/self.scale):
            dc.DrawLine(0, i*self.scale, self.width, i*self.scale)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)
        dc.SetUserScale(self.zoom, self.zoom)


class SketchFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Sketch Frame",
        size=(800,600))
        self.sketch = DrawingGridWindow(self, -1)

if __name__ == '__main__':
    app = wx.App()
    frame = SketchFrame(None)
    frame.Show(True)
    app.MainLoop()
