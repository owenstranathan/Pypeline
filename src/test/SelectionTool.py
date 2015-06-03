# RGB (Red, Green, Blue) intensity values for highlighted color: 255, 251, 204
# Opacity varies from 0 (Completely Translucent) to 256 (completely opaque)
# Opacity is the 4th parameter of color

import wx
import random


# Just Testing
list_of_nodes = []

for i in range(10):
    x, y = ((random.randint(0, 500)), (random.randint(0, 500)))
    list_of_nodes.append((x, y))

class SelectionTool(wx.Panel):


    def __init__(self, parent):
        super(SelectionTool, self).__init__(parent)
        self.SetBackgroundColour('WHITE')
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.overlay = wx.Overlay()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.selection_box = None
        self.selection_pos = None
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.pen = wx.Pen(wx.Colour(0, 0, 0, 200), 1)
        self.nodes = list_of_nodes

        # random lines for testing
        # self.lines = [(random.randint(100, 500) for i in range(2)) for j in range(10)]
        # print self.lines

    def OnErase(self, event):
        pass

    def on_size(self, event):

        ww, hh = self.GetClientSize()
        for i in range(10):
            x, y = ((random.randint(0, ww)), (random.randint(0, hh)))
            if (x,y) not in self.nodes:
                self.nodes.append((x, y))
        print self.nodes
        print len(self.nodes)
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        gc = wx.GCDC(dc)
        gc.SetPen(self.pen)
        gc.SetBrush(wx.Brush(wx.Colour(178,  34,  34, 110)))

        # draw diagonal line to test if event size is working
        # gc.DrawLine(0,0,w,h)
        for node in self.nodes:
            gc.DrawCircle(node[0], node[1], 5)

    def OnLeftDown(self, event):
        # reinitialize our selection box
        self.selection_box = None
        self.CaptureMouse()
        self.overlay = wx.Overlay()
        self.selection_pos = event.Position

    def OnMotion(self, event):
        if not self.HasCapture():
            return

        dc = wx.BufferedDC(wx.ClientDC(self))
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        gdc = wx.GraphicsContext_Create(dc)
        gdc.SetPen(wx.RED_PEN)
        gdc.SetBrush(wx.Brush(wx.Colour(178, 34, 34, 100)))
        gdc.DrawRectangle(*wx.RectPP(self.selection_pos, event.Position))
        del odc

    def OnLeftUp(self, event):

        if not self.HasCapture():
            return
        self.ReleaseMouse()
        self.release_pos = event.Position
        self.selection_pos_copy = self.selection_pos
        self.selection_pos = None
        self.overlay.Reset()
        # forces paint event, but whatever is being saved in DC should repaint ok.
        self.Refresh()
        self.isInSelectionRect()

    def isInSelectionRect(self):

        x_bounds = (min(self.selection_pos_copy[0], self.release_pos[0]), max(self.selection_pos_copy[0], self.release_pos[0]))
        # print x_bounds
        y_bounds = (min(self.selection_pos_copy[1], self.release_pos[1]), max(self.selection_pos_copy[1], self.release_pos[1]))
        # print y_bounds

        for i in self.nodes:
            if i[0] >= x_bounds[0] and i[0] <= x_bounds[1]:
                if i[1] >= y_bounds[0] and i[1] <= y_bounds[1]:
                    print "the coordinates are", i, "and Ian is a Boss"
        return

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('My Title')
        self.SetClientSize((500, 500))
        self.Center()
        self.view = SelectionTool(self)

def main():
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
