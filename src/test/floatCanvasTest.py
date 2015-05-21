import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

SCREEN_HEIGHT = 640
SCREEN_WIDTH = 800
grid_cell_size = 30

def YDownProjection(CenterPoint):
    return N.array((1,-1))

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

        self.firstClick = False
        self.lines = []


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
        self.Canvas.InitAll()
        self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.SetTitle('Simple menu')
        self.Centre()
        self.Show(True)


    def OnQuit(self, event):
        self.Close()

    ##LEFT CLICK EVENT HANDLER
    def onLeftDown(self, event):
        if self.firstClick is False:
            self.firstClick = True
            self.pos = self.getSnapPos(event.GetCoords())

            print self.pos
        else:
            self.lines.append((self.pos , self.getSnapPos(event.GetCoords())))
            if len(self.lines) != 0:
               self.pos = self.getSnapPos(event.GetCoords())

            event.Skip()

    def onKeyDown(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
           self.firstClick = False

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
        self.Canvas.AddArrowLine(coords, LineWidth=2, LineColor='BLUE', ArrowHeadSize=8)
        #self.Canvas.ZoomToBB()
        self.Canvas.Draw()
        self.Canvas.InitAll()
        for line in self.lines:
            self.Canvas.AddArrowLine(line, LineWidth=2, LineColor="GREEN", ArrowHeadSize=8  )

    def onWheel(self,event):
        pass

def main():

    ex = wx.App()
    Example(None, wx.ID_ANY, "TEST", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
