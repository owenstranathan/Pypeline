import wx
import random

class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, -1)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.lines = [[random.randint(0, 500) for i in range(4)] for j in range(100)]
        self.Bind(wx.EVT_MOUSEWHEEL, self.ScrollWheel)
        self.zoom = 1
        #self.dc = wx.BufferedDC(self)
        listlist = []

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        #dc = wx.GCDC(dc)
        print self.zoom
        dc.SetUserScale(self.zoom, self.zoom)
        for line in self.lines:
            dc.DrawLine(*line)

    def ScrollWheel(self, event):
            '''print "Mouse Wheel Moved in Frame"
            print "Wheel Rotation is:", event.GetWheelRotation()
            print "Wheel Delta is:", event.GetWheelDelta()'''
            sign = event.GetWheelRotation() / 120
            if(sign > 0):
                self.zoom = self.zoom * 1.05
                self.Refresh()
                #self.dc.SetUserScale(self.zoom, self.zoom)
            else:
                self.zoom = self.zoom * 0.95
                self.Refresh()
                #self.dc.SetUserScale(self.zoom, self.zoom)



        # wheel_rotation = event.GetWheelRotation
        # if wheel_rotation < 0:
        #     print "I like pie"
        # else:
        #     print 'I love men'
        #dc.SetUserScale(20, 20)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, -1, 'Test', size=(600, 400))

        Panel(self)


if __name__ == "__main__":
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()
