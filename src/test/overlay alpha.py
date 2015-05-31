# http://wxpython-users.1045709.n5.nabble.com/wx-Overlay-td2354977.html

# AutoBufferedPaintDC does not work with SetDoubleBuffered or GraphicsContext
# Flicker stopped after wrapping the ClientDC with a BufferedDC

import wx
import random

class OverlayPanel(wx.Panel):
    def __init__(self, parent):
        super(OverlayPanel, self).__init__(parent)
        self.SetBackgroundColour('WHITE')
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.overlay = wx.Overlay()
        self.selection_box = None
        self.selection_pos = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)

        # random lines for testing
        self.lines = [[random.randint(100, 500) for i in range(4)] for j in range(10)]
        print self.lines
        # self.SetDoubleBuffered(True)

    def OnErase(self, evt):
        pass

    def OnPaint(self, evt):

        # dc = wx.AutoBufferedPaintDC(self)
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        gc = wx.GCDC(dc)
        gc.SetPen(wx.Pen("black", 2))
        gc.SetUserScale(1.5, 1.5)

        for lines in self.lines:
            gc.DrawLine(*lines)

    def OnLeftDown(self, evt):
        # reinitialize our selection box
        self.selection_box = None
        self.CaptureMouse()
        self.overlay = wx.Overlay()
        self.selection_pos = evt.Position
        
    def OnLeftUp(self, evt):
        if not self.HasCapture():
            return
        self.ReleaseMouse()

        # rectangle saved in memory to use wx.Rect contain syntax
        self.selection_box = wx.RectPP(self.selection_pos, evt.Position)
        #self.selection_box.Contains(wx.Rect(x_min, y_min, x_max, y_max))
        self.selection_pos = None
        # clears overlay graphic
        self.overlay.Reset()
        # forces paint event, but whatever is being saved in DC should repaint ok.
        self.Refresh()
        
    def OnMotion(self, evt):
        if not self.HasCapture():
            return
        
        dc = wx.BufferedDC(wx.ClientDC(self))
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        gdc = wx.GraphicsContext_Create(dc)
        gdc.SetPen(wx.RED_PEN)
        gdc.SetBrush(wx.Brush(wx.Colour(178, 34, 34, 100)))
        gdc.DrawRectangle(*wx.RectPP(self.selection_pos, evt.Position))
        del odc

            
if __name__ == '__main__':
    app = wx.App(False)
    testFrame = wx.Frame(None)
    testPanel = OverlayPanel(testFrame)
    testFrame.Show()
    app.MainLoop()