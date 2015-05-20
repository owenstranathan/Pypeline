import wx


class DrawingGridWindow(wx.Window):
    def __init__(self, parent, ID):
        '''CALL PARENT CONSTRUCTOR'''
        wx.Window.__init__(self, parent, ID)

        '''INITIALIZE THE WINDOW'''
        self.SetBackgroundColour("WHITE")
        self.color = "Black"
        self.thickness = 1
        self.SetDoubleBuffered(True)
        size = self.GetClientSize()
        self.width, self.height = parent.GetSize()
        self.buffer = wx.EmptyBitmap(self.width, self.height)



        '''INITIALIZE DRAWING TOOLS'''
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)

        '''BIND EVENTS'''
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent) #MOUSE EVENTS
        #self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)    #KEYCLICK
        self.Bind(wx.EVT_PAINT, self.onPaint)  #PAINT
        self.Bind(wx.EVT_SIZE, self.onSize)    #RESIZE
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase) '''CLEARING BACKGROUND'''

        '''useful variables'''
        self.lines = []
        self.clicked = False
        self.grid_cell_size = 30
        self.zoom = 1

    '''MOUSE/////////////////////////////////////////////////////////////////'''
    def onMouseEvent(self, event):
        eventType = event.GetEventType()
        #print eventType
        '''switch through the event types'''
        if eventType == wx.EVT_LEFT_DOWN.evtType[0]:  #LEFT CLICK
            self.leftClick(event)

        elif event.Moving() and self.clicked:
            self.drawMotion(event)

        elif eventType == wx.EVT_MOUSEWHEEL.evtType[0]:
            self.onScroll(event)

        event.Skip()
        self.Refresh()


    def leftClick(self, event):
        if self.clicked is False:
            self.clicked = True
            self.pos = self.getSnapPos(event.GetPositionTuple())
        else:
            self.lines.append(self.pos + self.getSnapPos(event.GetPositionTuple()))
            if len(self.lines) != 0:
               self.pos = self.getSnapPos(event.GetPositionTuple())

    def drawMotion(self, event):
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetPen(wx.Pen("RED", 3, wx.SOLID))
        self.newPos = self.getSnapPos(event.GetPositionTuple())
        coords = self.pos + self.newPos
        dc.DrawLine(*coords)

    def onScroll(self, event):
        sign = event.GetWheelRotation() / 120
        if(sign > 0):
            self.zoom = self.zoom * 1.05

        else:
            self.zoom = self.zoom * 0.95


        #dc.SetUserScale(self.zoom, self.zoom)



    '''DRAWING///////////////////////////////////////////////////////////////'''

    def onPaint(self, event):
        pc = wx.AutoBufferedPaintDC(self)
        pc.SetUserScale(self.zoom, self.zoom)
        self.reDraw(pc)

    def reDraw(self, dc):
        dc.Clear()
        '''DRAW GRID'''
        dc.SetPen(self.pen)
        for i in range(0, int(self.width/self.grid_cell_size)):
            dc.DrawLine(i*self.grid_cell_size,0, i*self.grid_cell_size, self.height)
        for i in range(0, int(self.height/self.grid_cell_size)):
            dc.DrawLine(0, i*self.grid_cell_size, self.width, i*self.grid_cell_size)

        '''DRAW LINES'''
        dc.SetPen(wx.Pen("GREEN", 3, wx.SOLID))
        for line in self.lines:
            dc.DrawLine(*line)



    '''MISC UTILITIES////////////////////////////////////////////////////////'''
    def onSize(self, event):
        size = self.GetClientSize()
        self.width, self.height = size
        self.buffer = wx.EmptyBitmap(self.width, self.height)
        self.Refresh()

    '''Find the snap position relative to the grid size'''
    def getSnapPos(self, arg_pos):
        return (self.grid_cell_size* round(arg_pos[0]/self.grid_cell_size),
         self.grid_cell_size*round(arg_pos[1]/self.grid_cell_size))


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
