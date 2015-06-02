# CreateRadialGradientBrush (self, xo, yo, xc, yc, radius, oColor, cColor)
# Canvas.AddCircle(xy, D, LineWidth = lw, LineColor = colors[cl], FillColor = colors[cf])
# Canvas.AddText("Circle # %i"%(i), xy, Size = 12, BackgroundColor = None, Position = "cc")

import wx
import numpy as N
import UIGraph as UIG
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



def main():

    ex = wx.App()
    UIG.UIGraph(None, wx.ID_ANY, "TEST", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
