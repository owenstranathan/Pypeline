# TO DO
# Add main ribbon frame ------------ DONE
# Remove toggle button
# Add status bar '' ------------ DONE
# Add 3 panel split ''
#

from __future__ import division
import wx
import time
import os
import sys
import images
import wx.aui
import wx.dataview as dv
import ListCtrl

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))


sys.path.append(os.path.split(dirName)[0])

try:
    from agw import ribbon as RB
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.ribbon as RB

from wx.lib.embeddedimage import PyEmbeddedImage

# --------------------------------------------------- #
# Some constants for ribbon buttons
ID_CIRCLE = wx.ID_HIGHEST + 1
ID_CROSS = ID_CIRCLE + 1
ID_TRIANGLE = ID_CIRCLE + 2
ID_SQUARE = ID_CIRCLE + 3
ID_POLYGON = ID_CIRCLE + 4
ID_SELECTION_EXPAND_H = ID_CIRCLE + 5
ID_SELECTION_EXPAND_V = ID_CIRCLE + 6
ID_SELECTION_CONTRACT = ID_CIRCLE + 7
ID_PRIMARY_COLOUR = ID_CIRCLE + 8
ID_SECONDARY_COLOUR = ID_CIRCLE + 9
ID_DEFAULT_PROVIDER = ID_CIRCLE + 10
ID_AUI_PROVIDER = ID_CIRCLE + 11
ID_MSW_PROVIDER = ID_CIRCLE + 12
ID_MAIN_TOOLBAR = ID_CIRCLE + 13
ID_POSITION_TOP = ID_CIRCLE + 14
ID_POSITION_TOP_ICONS = ID_CIRCLE + 15
ID_POSITION_TOP_BOTH = ID_CIRCLE + 16
ID_POSITION_LEFT = ID_CIRCLE + 17
ID_POSITION_LEFT_LABELS = ID_CIRCLE + 18
ID_POSITION_LEFT_BOTH = ID_CIRCLE + 19
ID_TOGGLE_PANELS = ID_CIRCLE + 20

# --------------------------------------------------- #
# Some bitmaps for ribbon buttons

align_center = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAADpJ"
    "REFUKJFjZGRiZqAEMFGkm4GBgQWZ8//f3//EaGJkYmaEsyn1Ags2QVwuQbaZNi4YDYMRGwYU"
    "ZyYAopsYTgbXQz4AAAAASUVORK5CYII=")

#----------------------------------------------------------------------
align_left = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAADxJ"
    "REFUKJFjZGRiZqAEMFGkm4GBgYWBgYHh/7+//4lRzMjEzIghRqkX8LoAm430dQExLhoNg2ER"
    "BhRnJgDCqhhOM7rMkQAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
align_right = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAADdJ"
    "REFUKJFjZGRiZqAEMFGkm4GBgQWb4P9/f/8To5mRiZmRkVIvYHUBsS6inQtGw2DEhQHFmQkA"
    "gowYTpdfxvkAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
aui_style = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAMFJ"
    "REFUWIXtlrENgzAUBQ/beAQWYAcGYYIkgyWZxz2lF0CiRwJBCmKJIlGq+DV+lS1ZutO39eSq"
    "MpaU5+O+kyGX661Ka3eG932fgw+wJwmTi/gtRcCdN9u2aQWWZdEKzPOsFVjXVSsguYJz++Wc"
    "QOI6gLZtAZimKQs88WKMh0CMMQv4UxxA0zQS+DiOh4D3XiIA7wkYo2tkB2Ct/XXuvwJ1XWsF"
    "5BOQv4FhGLQCXddJ4CEE/Y+oCBSBIlAEHByNpMoLu1w1qHGIod8AAAAASUVORK5CYII=")

#----------------------------------------------------------------------
auto_crop_selection = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAi5J"
    "REFUWIXFlz1r20AYx/+ns4PjR7jG1IgG2tIO/QAdkyyZOvcrlECnQujWT9AtFDIF+h06dcjU"
    "KaFTxg4dWwiIBNU1d8Y0Ol0H+8TpxUKKpOgPB7Is7vfoebtHjDkcXcrplA4AzOFYe0ED0Pd9"
    "zUwIdKQ0czhr/Y3XMjxWlAP3YVScAzpSOg0/9g8z95uS2Tc3CQ0cAE5vjuKH2zAmNsC42oYT"
    "d0Gc8OXvR+hI6TNx0pgRhpebhDpS+vTmCMQJ5LgAgOHamP3tN2giLwwvNwTM4eztw08ZOHG3"
    "LjejTAjs368ffEjAyaHGwIZXWAVn4qQVeIJnd0Jzne6O9ko/Q/vfM/fKLKQ7YVXRwaWeTAZw"
    "iUNIhSBYQn57WTk579SK6eBSP3lM2PG2MB71MJuHuPL/4ddvWdoIw+tVtRgAJpMBdrwtPH86"
    "gDftw7++BQAIqSAr7rWxCjZpuHuuXeIYj3rwpn28eLYNb9rHeNSDSxzD3fNSjcrwYg+UDcHi"
    "Yo+JRz/0bB7Gb+5f32I2DyGkwuJir/0QBMESV7TKneBPGOdAECwr79V5FRT2gTIrrw+gRP9A"
    "ug80NXzoSOmf4VcAgIwkpBKQSuKV+y6R6JnDqOnJpwhu8zaeBU3BF0rE84T9TOFEVNsAC74y"
    "SCQmK1uthMC43cClWnnEnjELJ6K6MnuZyUquPfHe+5wY/ZjDWe0yLHPsHvuHmVJE3eP4Lh7J"
    "+6+VKkgrD547EaHLb8Ou9B/kXYasrB2oNQAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
auto_crop_selection_small = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAASRJ"
    "REFUOI2lkzFLw1AUhb+XdOvQiiAqgqAgLeJSWo0RG+iiOBRcXV3t6OIPEHfnQPUPFERxExRK"
    "i7gLXUSoo4hDxuQ62AsSQxPaAw8u7753OOdwrwGECWEs2+S0AJAoFK3TIFEoAJZerDhz0uo0"
    "kSgUbWZBTtkOTmtseRvM3y0y6A65vrjPRGCphcvDG957n3iNTfJ2PquAXwWKQXfIR/+Ll6dX"
    "AAqOL9/949RMxFg28VN02+KcvEnRbSf29Z+VxFhwfClVPPYbM5QqHgXHHxvqVArMqEj0qRnU"
    "dtelWi8ThAFX57cYyzY6M4kWFBpgtV7m6GyPtZ2lf2/GEiiCMODx4Znl7Vl02FIziPsFpNVp"
    "yqq7IJkziOPvrmhtmHIbzUjOxPgBMl93hZvH4+AAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
circle = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAANtJ"
    "REFUWIXNV8sSxCAIA/z/T67d0864PiBQ2ZpbHQkxlGKZpVAEtV53+yxSOMLDqIA+oQVUkCnA"
    "m9grRDKTIxxLAUhykcKI1RrXtARagJXQGzsIWBF433KU50fALCjaXiinoBujmHG0udQu+AeE"
    "KO/0Gtc35xkODIsbT29xvu/Ajs9tFLVe9+BAhv0a9/sl6BcySzJv90TLLYgUPq8ERDllWE7H"
    "3Ym8ECJ7Yj2FNmvOcIAozwVr0p51JbOCESGPL6UIUU/o2QsLQIkRaK6pXZB1KW1x/s8pKijq"
    "1gcd75B9JbWfpAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
circle_small = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAHxJ"
    "REFUOI2lU0EOwCAIg/r/J6u7TKMVgWXcDG2paFVRxKrWal/PQFELpyzARC4WQjSVCYyZDtbG"
    "za6FQZbMvcHBDZARERFBtDSvWqt9OshMt7DwgCmx1U6WtC/9g/VjOoq6HymaLvJewXrfiDw4"
    "WxZuAfKC9TtMh0DkhusBDWJQP2fEFKMAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
colours = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAA3NCSVQICAjb4U/gAAAAOklE"
    "QVQokWNgIBEwMjAwXJJiwpTQefgPU5CJlQGLUvxgRGpgYWBgiNiHReJu3H9s6hkHoR8GoQaS"
    "AQBoQQZvRwyakAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
cross = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAO9J"
    "REFUWIXNl9sOAyEIRIHu/39xU/epiXVRhltSX3ZNZOZoDCCzvGge4/MeLBdTw9C0ZV0wf6vN"
    "NW1ZF+zmFebaXE5mFRCWNhMN0yR6J5ANCCIeOQkkhuVi+f5UQqDmRNMlrILwmP8AVEB4zR8A"
    "GYiIuQoQgYiaExHxmop3Jplx2pB6AkhghbkJkIVAYk2AKAQaAwF4ITxrYYCuAQNUp2IXQFcx"
    "ggAyuQAqx13mqMYWAE2v2QKmAnhzewbiARAtLFEItS33mmcgtm151MALcWzLvcIRiP9vyzvL"
    "sdmWdzYkZlte+UI+aattecfzfKd9AzzryGWicE3pAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
empty = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAA3NCSVQICAjb4U/gAAAANElE"
    "QVQokWNgIBEwMjAw/P//H84/efIkHtUWFhZMpNpAew0sDKjuNjc3H2gnjWqgiQaSAQBRvgke"
    "qvN6jAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
expand_selection_h = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAVFJ"
    "REFUWIXtVjFuwzAMJCmjQGrv/UH27vlB9j4gyAvykC5eCz+gewbv3rvnB93lGihCsUNqQ1Ys"
    "x0nUJgZ8AGFapOgTKVFGJAW3BN306xOBURIQwyKGpU//UwIAAEgK66etXxRrdMewL83/VoKQ"
    "uL8SnNrN19i67OQ65Tr1070SuU6PSDYExLAUVdYiY0s93nfcbJtvflFlLRKIpEAMy8f3O5Ss"
    "oeQSvlhDaQ56yRo2T29NcDEsPhK2TQzL6+caYpVArGKIKYHHWlcJPD+8AJJCEsOy228HJjEc"
    "dvstiGE5+xgOLcFQEJLCebQcPCFUI5pHywNhJAW/vUCKKpNcpwIAR2L71borrp8ruU6lqLJW"
    "vKYESAoXsxXY77bY475VuX5d8xezVdvP7YR1Gofs9HNtXXGjvlWEhC/u/d0FpzBdx6ExzhL4"
    "/ooviTW+EkwEQuMHDB37+4Mc8HwAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
expand_selection_v = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAATtJ"
    "REFUWIXtlzGOwjAQRb8dhISCRMkN6OnpKaho9gArWho6TkBHQ4v2ADRbpaCnp88NtlyJCAnF"
    "HqqAozhoPfEmIPElS04cj59mbE9GCBmAK9KKAEDIQHBtyCqLx2mEOI1uIBwJjgdIKzpedrl3"
    "w/YHyxPOAKQVHc5f1rFR59MZwgmAtKL9afPwm3F37gThDJD1v39XubFpb3k36gDQ+vPqhmHS"
    "ihJ9Kh13kROAqUQl3Km+AIoe4Ih9DK3G6jiGvsW+Cb1JyKDQABAA+q9+rtlCQFpRlQRTJpvd"
    "59wDVbLbI9nsNr4J3yEoDUH2MWlFvvq2dZ4zBHWKlQ19JiN2Ol7/zHLPi/6WZYcNEAZd7lRf"
    "AGH9AGbsQ1n0AKdSeq3f8gyiscLEhGisNDMh4jQCAAxaE3aFXOkq9lGeXwGxGs15gJjjygAA"
    "AABJRU5ErkJggg==")

#----------------------------------------------------------------------
eye = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAJNJ"
    "REFUOI3NkjEOwjAQBOdsoE7pwj+gyCP4f0HBD67gDUHJUkRGhkRIlgtYyZJ13h3pzmcWIj0K"
    "Xem/ABw+C1pmfQtYiLYLKEF3ByDnDGlaH++nuq4aZBYiWmYVQx0ez0cArrfHG6R4CkTu/jqA"
    "SJPGiwSDYFjvadKet3uI3S1Y2cSGIbIZYq3Wb9wAWvX7Ve4GPAEieGRem+OF/wAAAABJRU5E"
    "rkJggg==")

#----------------------------------------------------------------------
hexagon = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAALNJ"
    "REFUWIXt180NgCAMBlALG7ILU7gLGxo9aWL4a/uV6KE9Q/sAxUoU4vZlBGRyjuXMsZxIDtLs"
    "QK/ofiRaCuCuVgJhAWYrRnZkCJAm1kCaAPSMJfNfAMuHi5vvAbQGawtzIHduohCrAVaFZ5D9"
    "SFRdRKuK93JDN6FFOMABDnCAAyoA2mSOopX7H5/j0UAEImpIpBPRwkOAFmLWlEoTL2vLuRBN"
    "YRVgBln+a9aDIK8rBLCICxjaeOXhD450AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
msw_style = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAOhJ"
    "REFUWIVjZGRiZkAGU3c8+c9AQ5DtIcOIzGdBtzzaSoCW9jMw7HjyH9kRjLAQmLrjyf8oS37a"
    "Wg4Fy45/hIcESgj8+UcX+1EAigN+/x1gB/yjafIbdQARDvg/AA5gZGRiZpi648l/D31+BkZG"
    "whqoAf7/Z2DYcRGSFRl7Nj36H2QuQh+b0cC6k28YmAbEZiTAwsDAwPD0xfMBsp4V4gAJUfGB"
    "sf/hO4gD/vwdgDIYCgaHA778+DOwDvg7EEUgsgPoVgLhcgDjiHfAaBQMuANGo2DAQ+De6+8D"
    "5oABb5CMOgDaJBu4NAAAvuND/BvGPIIAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
position_left = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAExJ"
    "REFUKJHtkzEKwDAMA0/yx/z/P7XqVOiQDmmHLDEIBEKCGyy5yHmEDyeXACIX3YlcPP2dvQkI"
    "QEblqYFRuTuZGtgIG2EpguR/33gBsoRzDlCsBR0AAAAASUVORK5CYII=")

#----------------------------------------------------------------------
position_top = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAFJJ"
    "REFUKJHtkzEKwDAMA092H5b//ylRppRCpzhToTd50RljJEXi0U0BRQrAiqQ1W5HszIABXAkr"
    "kltQCb8E3z1By1Llev5zF4/uONkO8AtAp22caOhgKT6Nla4AAAAASUVORK5CYII=")

#----------------------------------------------------------------------
ribbon = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAYxJ"
    "REFUOI19krtKA0EUhr8xMcYbRIJgk87KBSsRBK0UROMi6y3Wig+wpLQTLMUHsLNSBEVCIoKd"
    "gpAyEBBMISKIiDeSmLhqxiLuZrPjeqrhXH6+c/4RoiWAX2iGKQHyR9vCryf43+D4zBLWtwTw"
    "FRJeAs0wpbEQ5+4Jql8BIl1tTu385EARCXqHB0bihIKwuxH+zdZY2xQIIRibWgSQbpEWL1Jf"
    "j+S5VH/ryQp6ssLOuvS5gItAM0w5ObtMb1eRd6ueS221O0JVq41wKKhQOAT5o21xerzHQ7GV"
    "SGeDwI630ge1mlTuoKzQHQ5RsRppPVkhtdVOTcJb+UNZ4U8XVlfmuX385LX0xUu5UStkM4oL"
    "ioAtAqDP6Vzff3N1mXHW9PYqH0kzTDk0bhDpCJE63AdgQk/wWr+s/JdAM0zZPzzt4E7oCQDO"
    "Uvu4826RJhsHR+O8Ww3Pbx6KynqDo/EmkiYbcxdpYlFBIZtRBgvZDLGoIHeR/pvAFrHVNcOU"
    "sWi9r+Cp+d7AHbYTHnElfgAFJbH0Sf7mkQAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
selection_panel = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAHlJ"
    "REFUOI3tk8EOwzAIQx+w307Dtu9u3UsS9bamuc4Ski8GjIyZByvwJTVA20CAnvBXb5SZAHp/"
    "vla3ol9cx666FWEemAeZqc7vVmbKzAMdu8zDZqx3zThiW28KdSvydsip6VfN30LYUhJHDrof"
    "gEvibvHR4CmWv/EExjdqKKO2QxEAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
square = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAEdJ"
    "REFUWIXt1zEOACAIQ9FC9P4HNinOuhsGPyNLXxoWouRS42RnOABJGvcic8bLQHsdN9feAAAA"
    "AAAAAAAAAAAAAILf8HvABvIMCjlFTCZ2AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
triangle = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAALFJ"
    "REFUWIXVl0EOgCAMBFvq/39s8ERCyCKwIJY9EYG2M9GDqsGETbzvKCKiZsrWCHT3RaEHSPTl"
    "etsAq0INgIhZC+cZyEnVTPMvgLFwloGSHq1HLZxjoEaPno1YOMNAix7t9Vrwb6CXHp3pseDb"
    "wCg9Otuy4NcAS4/uvFnwaWCWHt2tWfBnYBU9qoEs+DKwmh7VKi34MfAVPaqZ9/JhYObPhk3q"
    "eb1t7ohKlO30eX5/Bx4qMXoN5ex1NgAAAABJRU5ErkJggg==")

# --------------------------------------------------- #

def CreateBitmap(xpm):

    bmp = eval(xpm).Bitmap

    return bmp


# --------------------------------------------------- #

class ColourClientData(object):

    def __init__(self, name, colour):

        self._name = name
        self._colour = colour


    def GetName(self):

        return self._name


    def GetColour(self):

        return self._colour

class CustomStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)

        # This status bar has three fields
        self.SetFieldsCount(3)
        # Sets the three fields to be relative widths to each other.
        self.SetStatusWidths([-2, -1, -2])

        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Field 0 ... just text
        self.SetStatusText("A Custom StatusBar...", 0)

        # This will fall into field 1 (the second field)
        self.cb = wx.CheckBox(self, 1001, "toggle clock")
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleClock, self.cb)
        self.cb.SetValue(True)

        # set the initial position of the checkbox
        self.Reposition()

        # We're going to use a timer to drive a 'clock' in the last
        # field.
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()


    # Handles events from the timer we started in __init__().
    # We're using it to drive a 'clock' in field 2 (the third field).
    def Notify(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
        self.SetStatusText(st, 2)



    # the checkbox was clicked
    def OnToggleClock(self, event):
        if self.cb.GetValue():
            self.timer.Start(1000)
            self.Notify()
        else:
            self.timer.Stop()


    def OnSize(self, evt):
        evt.Skip()
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True


    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()


    # reposition the checkbox
    def Reposition(self):
        rect = self.GetFieldRect(1)
        rect.x += 1
        rect.y += 1
        self.cb.SetRect(rect)
        self.sizeChanged = False
# --------------------------------------------------- #

########################################################################

class TestAuiPanel(wx.Panel):
    """ Simple class example for wx.aui.AuiNotebook. """

    def __init__(self, parent):
        """ Class constructor. """

        wx.Panel.__init__(self, parent, -1)

        # Create the wx.aui.AuiNotebook
        self.nb = wx.aui.AuiNotebook(self)

        # Create a simple text control
        page = wx.TextCtrl(self.nb, -1, "Design/Map Screen", style=wx.TE_MULTILINE)
        # Add the text control as wx.aui.AuiNotebook page
        self.nb.AddPage(page, "Design-1")

        # Add some more pages to the wx.aui.AuiNotebook
        for num in range(1, 5):
            page = wx.TextCtrl(self.nb, -1, "This is page %d" % num, style=wx.TE_MULTILINE)
            self.nb.AddPage(page, "Tab Number %d" % num)

        # Put the wx.aui.AuiNotebook in a sizer and
        # assign the sizer to the main panel
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

########################################################################

class TestSearchCtrl(wx.SearchCtrl):
    maxSearches = 5

    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=(210, 20), style=wx.SUNKEN_BORDER,
                 doSearch=None):
        style |= wx.TE_PROCESS_ENTER
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEntered)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuItem, id=1, id2=self.maxSearches)
        self.doSearch = doSearch
        self.searches = []

    def OnTextEntered(self, evt):
        text = self.GetValue()
        if self.doSearch(text):
            self.searches.append(text)
            if len(self.searches) > self.maxSearches:
                del self.searches[0]
            self.SetMenu(self.MakeMenu())
        self.SetValue("")

    def OnMenuItem(self, evt):
        text = self.searches[evt.GetId()-1]
        self.doSearch(text)

    def MakeMenu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for idx, txt in enumerate(self.searches):
            menu.Append(1+idx, txt)
        return menu

########################################################################

# Pipe Flow Equation Choose

class SingleChoice(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        sampleList = ['Choose Flow Eq.', 'General Pipe Eq.', 'Weymouth Eq.', 'Aga Eq.', 'Panhandle A Eq.',
                      'Panhandle B Eq.', 'IGT Eq.', 'Spitzglass (HP) Eq.']

        self.ch = wx.Choice(self, -1, (20, 50), (130, 50),choices = sampleList)
        self.ch.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.ch)


    def EvtChoice(self, event):
        self.log.WriteText('EvtChoice: %s\n' % event.GetString())
        self.ch.Append("A new item")

        if event.GetString() == 'one':
            self.log.WriteText('Well done!\n')

########################################################################


class ListModel(dv.PyDataViewIndexListModel):
    def __init__(self, data):
        dv.PyDataViewIndexListModel.__init__(self, len(data))
        self.data = data


    # All of our columns are strings.  If the model or the renderers
    # in the view are other types then that should be reflected here.
    def GetColumnType(self, col):
        return "string"

    # This method is called to provide the data object for a
    # particular row,col
    def GetValueByRow(self, row, col):
        return self.data[row][col]

    # This method is called when the user edits a data item in the view.
    def SetValueByRow(self, value, row, col):
        self.data[row][col] = value

    # Report how many columns this model provides data for.
    def GetColumnCount(self):
        return len(self.data[0])

    # Report the number of rows in the model
    def GetCount(self):

        return len(self.data)

    # Called to check if non-standard attributes should be used in the
    # cell at (row, col)
    def GetAttrByRow(self, row, col, attr):

        if col == 3:
            attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False


    # This is called to assist with sorting the data in the view.  The
    # first two args are instances of the DataViewItem class, so we
    # need to convert them to row numbers with the GetRow method.
    # Then it's just a matter of fetching the right values from our
    # data set and comparing them.  The return value is -1, 0, or 1,
    # just like Python's cmp() function.
    def Compare(self, item1, item2, col, ascending):
        if not ascending: # swap sort order?
            item2, item1 = item1, item2
        row1 = self.GetRow(item1)
        row2 = self.GetRow(item2)
        if col == 0:
            return cmp(int(self.data[row1][col]), int(self.data[row2][col]))
        else:
            return cmp(self.data[row1][col], self.data[row2][col])


    def DeleteRows(self, rows):
        # make a copy since we'll be sorting(mutating) the list
        rows = list(rows)
        # use reverse order so the indexes don't change as we remove items
        rows.sort(reverse=True)

        for row in rows:
            # remove it from our data structure
            del self.data[row]
            # notify the view(s) using this model that it has been removed
            self.RowDeleted(row)


    def AddRow(self, value):
        # update data structure
        self.data.append(value)
        # notify views
        self.RowAppended()

class ListPanel(wx.Panel):


    def __init__(self, parent, model=None, data=None):
        wx.Panel.__init__(self, parent, -1)

        # Create a dataview control
        self.dvc = dv.DataViewCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES # nice alternating bg colors
                                   #| dv.DV_HORIZ_RULES
                                   | dv.DV_VERT_RULES
                                   | dv.DV_MULTIPLE
                                   )

        # Create an instance of our simple model...
        if model is None:
            self.model = ListModel(data)
        else:
            self.model = model

        # ...and associate it with the dataview control.  Models can
        # be shared between multiple DataViewCtrls, so this does not
        # assign ownership like many things in wx do.  There is some
        # internal reference counting happening so you don't really
        # need to hold a reference to it either, but we do for this
        # example so we can fiddle with the model from the widget
        # inspector or whatever.
        self.dvc.AssociateModel(self.model)

        # Now we create some columns.  The second parameter is the
        # column number within the model that the DataViewColumn will
        # fetch the data from.  This means that you can have views
        # using the same model that show different columns of data, or
        # that they can be in a different order than in the model.
        self.dvc.AppendTextColumn("Title",  1, width=110, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Type",   2, width=38, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Label",   3, width=60,  mode=dv.DATAVIEW_CELL_EDITABLE)

        # There are Prepend methods too, and also convenience methods
        # for other data types but we are only using strings in this
        # example.  You can also create a DataViewColumn object
        # yourself and then just use AppendColumn or PrependColumn.
        c0 = self.dvc.PrependTextColumn("Id", 0, width=30)

        # The DataViewColumn object is returned from the Append and
        # Prepend methods, and we can modify some of it's properties
        # like this.
        c0.Alignment = wx.ALIGN_RIGHT
        c0.Renderer.Alignment = wx.ALIGN_RIGHT
        c0.MinWidth = 40

        # Through the magic of Python we can also access the columns
        # as a list via the Columns property.  Here we'll mark them
        # all as sortable and reorderable.
        for c in self.dvc.Columns:
            c.Sortable = True
            c.Reorderable = True

        # Let's change our minds and not let the first col be moved.
        c0.Reorderable = False

        # set the Sizer property (same as SetSizer)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)

        # Add some buttons to help out with the tests
        b1 = wx.Button(self, label="View",size=(40,20), name="newView")
        self.Bind(wx.EVT_BUTTON, self.OnNewView, b1)
        b2 = wx.Button(self, label="Add Node",size=(65,20))
        self.Bind(wx.EVT_BUTTON, self.OnAddRow, b2)
        b3 = wx.Button(self, label="Del Node",size=(65,20))
        self.Bind(wx.EVT_BUTTON, self.OnDeleteRows, b3)

        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(b1, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(b2, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(b3, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)


    def OnNewView(self, evt):
        f = wx.Frame(None, title="Wide view", size=(600,400))
        ListPanel(f, self.model)
        b = f.FindWindowByName("newView")
        b.Disable()
        f.Show()


    def OnDeleteRows(self, evt):
        # Remove the selected row(s) from the model. The model will take care
        # of notifying the view (and any other observers) that the change has
        # happened.
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        self.model.DeleteRows(rows)


    def OnAddRow(self, evt):
        # Add some bogus data to a new row in the model's data
        id = len(self.model.data) + 1
        value = [str(id),
                 'New Title %d' % id,
                 'New Type %d' % id,
                 'New Label %d' % id]
        self.model.AddRow(value)


#----------------------------------------------------------------------
    #
    # musicdata = ListCtrl.musicdata.items()
    # musicdata.sort()
    # musicdata = [[str(k)] + list(v) for k,v in musicdata]
    #
    # win = TestPanel(nb, log, data=musicdata)
    # return win


########################################################################


class RadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )
        panel = wx.Panel(self, -1 )

        # Layout controls on panel:
        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox( panel, -1, "" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=2 )

        # 1st group of controls:
        self.group1_ctrls = []
        radio1 = wx.RadioButton( panel, -1, " Beni Sec ", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, " Beni Sec " )
        radio3 = wx.RadioButton( panel, -1, " Beni Sec " )
        text1 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        text2 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        text3 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        self.group1_ctrls.append((radio1, text1))
        self.group1_ctrls.append((radio2, text2))
        self.group1_ctrls.append((radio3, text3))

        for radio, text in self.group1_ctrls:
            grid1.Add( radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)

        box2_title = wx.StaticBox( panel, -1, "Choose Method" )
        box2 = wx.StaticBoxSizer( box2_title, wx.VERTICAL )
        grid2 = wx.FlexGridSizer( cols=2 )

        # 2nd group of controls:
        self.group2_ctrls = []
        radio4 = wx.RadioButton( panel, -1, " Beni Sec ", style = wx.RB_GROUP )
        radio5 = wx.RadioButton( panel, -1, " Beni Sec " )
        radio6 = wx.RadioButton( panel, -1, " Beni Sec " )
        text4 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        text5 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        text6 = wx.TextCtrl( panel, -1, "Bana Yaz" )
        self.group2_ctrls.append((radio4, text4))
        self.group2_ctrls.append((radio5, text5))
        self.group2_ctrls.append((radio6, text6))

        for radio, text in self.group2_ctrls:
            grid2.Add( radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid2.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        box2.Add( grid2, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box2, 0, wx.ALIGN_CENTRE|wx.ALL, 2)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (5,50) )
        self.panel = panel

        # Setup event handling and initial state for controls:
        for radio, text in self.group1_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, radio )

        for radio, text in self.group2_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup2Select, radio )

        for radio, text in self.group1_ctrls + self.group2_ctrls:
            radio.SetValue(0)
            text.Enable(False)

    def OnGroup1Select( self, event ):
        radio_selected = event.GetEventObject()

        for radio, text in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
            else:
                text.Enable(False)

    def OnGroup2Select( self, event ):
        radio_selected = event.GetEventObject()

        for radio, text in self.group2_ctrls:
            if radio is radio_selected:
                text.Enable(True)
            else:
                text.Enable(False)


########################################################################
class SpinPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        wx.StaticText(self, -1, "", pos=(25,25))
        spin = wx.SpinCtrlDouble(self, value='0.00', pos=(75,50), size=(54,-1),style=wx.SP_ARROW_KEYS,
                                 min=0.05, max=0.95, inc=0.05)
        spin.SetDigits(2)


# class SpinPanel(wx.Panel):
#     def __init__(self, parent):
#         wx.Panel.__init__(self, parent, -1)
#         self.count = 0
#
#         self.text = wx.TextCtrl(self, -1, "1", (30, 50), (30, -1))
#         h = self.text.GetSize().height
#         w = self.text.GetSize().width + self.text.GetPosition().x + 2
#
#         self.spin = wx.SpinButton(self, -1,
#                                   (w, 50),
#                                   (h*2/3, h),
#                                   wx.SP_VERTICAL)
#
#         self.spin.SetRange(0.1, 10.0)
#         self.spin.SetValue(0.1)
#
#         self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)
#
#
#     def OnSpin(self, event):
#         self.text.SetValue(str(event.GetPosition()))


########################################################################
class TabPanel(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)


        txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")
        choicebox = SingleChoice(self,-1)

        # self._logwindow = wx.TextCtrl(panel, wx.ID_ANY, "", wx.DefaultPosition, size=(210, 20), style=wx.SUNKEN_BORDER)

        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]
        win = ListPanel(self, None, data=nodedata)
        spinbutton =  SpinPanel(self)
        radiobutton = RadioPanel(self)



        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(win, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sizer2, 3, wx.ALL, 5)

        sizer2.Add(txtOne, 0, wx.ALL, 5)
        sizer2.Add(txtTwo, 0, wx.ALL, 5)
        sizer2.Add(spinbutton, 0, wx.ALL, 5)
        sizer2.Add(choicebox, 0, wx.ALL, 5)
        sizer2.Add(radiobutton, 0, wx.ALL, 5)

        self.SetSizer(sizer)


########################################################################

class NotebookDemo(wx.Notebook):
    """
    Notebook class
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, size=(210, 30), style=
                             wx.BK_TOP
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )
        # Create the first tab and add it to the notebook
        tabOne = TabPanel(self)
        tabOne.SetBackgroundColour("Red")
        self.AddPage(tabOne, "ND")

        # Show how to put an image on one of the notebook tabs,
        # first make the image list:
        il = wx.ImageList(16, 16)
        idx1 = il.Add(images.Smiles.GetBitmap())
        self.AssignImageList(il)

        # now put an image on the first tab we just created:
        self.SetPageImage(0, idx1)

        # Create and add the second tab
        tabTwo = TabPanel(self)
        tabTwo.SetBackgroundColour("Green")
        self.AddPage(tabTwo, "PP")

        # Create and add the third tab
        tabThree = TabPanel(self)
        tabThree.SetBackgroundColour("Blue")
        self.AddPage(tabThree, "GG")

        self.AddPage(TabPanel(self), "VV")
        self.AddPage(TabPanel(self), "CP")
        self.AddPage(TabPanel(self), "RG")
        self.AddPage(TabPanel(self), "LE")
        self.AddPage(TabPanel(self), "HC")
        self.AddPage(TabPanel(self), "LS")


    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

########################################################################

# For every functionality panel within the ribbon toolbar... create panel and corresponding sizer

class RibbonFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, log=None):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

        panel = wx.Panel(self)
        #NOTE
        # in init assign wx.lib.agw.ribbon.RibbonBar afterwhich you can add pages to with wx.lib.agw.ribbon.RibbonPage
        self._ribbon = RB.RibbonBar(panel, wx.ID_ANY, agwStyle=RB.RIBBON_BAR_DEFAULT_STYLE|RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)

        self._bitmap_creation_dc = wx.MemoryDC()
        self._colour_data = wx.ColourData()

        home = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Examples", CreateBitmap("ribbon"))
        toolbar_panel = RB.RibbonPanel(home, wx.ID_ANY, "", wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE|RB.RIBBON_PANEL_EXT_BUTTON)

        # The panel that the Ribbon toolbar takes has to be called wx.lib.agw.ribbon.RibbonPanel
        # Can create toolbar as wx.lib.agw.ribbon.Toolbar(wx.lib.agw.ribbon.RibbonPanel, id)
        toolbar = RB.RibbonToolBar(toolbar_panel, ID_MAIN_TOOLBAR)


        # Adding toolbar items (tools)is just like normal... assigned toolbar.AddTool(id
        toolbar.AddTool(wx.ID_ANY, CreateBitmap("align_left"))
        toolbar.AddTool(wx.ID_ANY, CreateBitmap("align_center"))
        toolbar.AddTool(wx.ID_ANY, CreateBitmap("align_right"))

        toolbar.AddSeparator()
        toolbar.AddHybridTool(wx.ID_NEW, wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_OTHER, wx.Size(16, 15)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, wx.Size(16, 15)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(16, 15)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, wx.Size(16, 15)))

        toolbar.AddSeparator()
        toolbar.AddDropdownTool(wx.ID_UNDO, wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_OTHER, wx.Size(16, 15)))
        toolbar.AddDropdownTool(wx.ID_REDO, wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_OTHER, wx.Size(16, 15)))

        toolbar.AddSeparator()
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, wx.Size(16, 15)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER, wx.Size(16, 15)))

        toolbar.AddSeparator()
        toolbar.AddHybridTool(ID_POSITION_LEFT, CreateBitmap("position_left"), "Align ribbonbar vertically\non the left\nfor demonstration purposes")
        toolbar.AddHybridTool(ID_POSITION_TOP, CreateBitmap("position_top"), "Align the ribbonbar horizontally\nat the top\nfor demonstration purposes")

        toolbar.AddSeparator()
        toolbar.AddHybridTool(wx.ID_PRINT, wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_OTHER, wx.Size(16, 15)),
                              "This is the Print button tooltip\ndemonstrating a tooltip")
        toolbar.SetRows(2, 3)


        # This is new panel selection

        selection_panel = RB.RibbonPanel(home, wx.ID_ANY, "", CreateBitmap("selection_panel"))
        selection = RB.RibbonButtonBar(selection_panel)
        selection.AddSimpleButton(ID_SELECTION_EXPAND_V, "Expand Vertically", CreateBitmap("expand_selection_v"),
                                  "This is a tooltip for Expand Vertically\ndemonstrating a tooltip")
        selection.AddSimpleButton(ID_SELECTION_EXPAND_H, "Expand Horizontally", CreateBitmap("expand_selection_h"), "")
        selection.AddButton(ID_SELECTION_CONTRACT, "Contract", CreateBitmap("auto_crop_selection"),
                                  CreateBitmap("auto_crop_selection_small"))



        # This is new panel shapes

        shapes_panel = RB.RibbonPanel(home, wx.ID_ANY, "", CreateBitmap("circle_small"))
        shapes = RB.RibbonButtonBar(shapes_panel)
        shapes.AddButton(ID_CIRCLE, "Circle", CreateBitmap("circle"), CreateBitmap("circle_small"),
                         help_string="This is a tooltip for the circle button\ndemonstrating another tooltip",
                         kind=RB.RIBBON_BUTTON_TOGGLE)
        shapes.AddSimpleButton(ID_CROSS, "Cross", CreateBitmap("cross"), "")
        shapes.AddHybridButton(ID_TRIANGLE, "Triangle", CreateBitmap("triangle"))
        shapes.AddSimpleButton(ID_SQUARE, "Square", CreateBitmap("square"), "")
        shapes.AddDropdownButton(ID_POLYGON, "Other Polygon", CreateBitmap("hexagon"), "")


        # This is new panel sizers


        sizer_panel = RB.RibbonPanel(home, wx.ID_ANY, "",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)

        strs = ["Item 1 using a box sizer now", "Item 2 using a box sizer now"]
        sizer_panelcombo = wx.ComboBox(sizer_panel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize,
                                       strs, wx.CB_READONLY)

        sizer_panelcombo2 = wx.ComboBox(sizer_panel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize,
                                        strs, wx.CB_READONLY)

        sizer_panelcombo.Select(0)
        sizer_panelcombo2.Select(1)
        sizer_panelcombo.SetMinSize(wx.Size(150, -1))
        sizer_panelcombo2.SetMinSize(wx.Size(150, -1))

        # not using wx.WrapSizer(wx.HORIZONTAL) as it reports an incorrect min height
        sizer_panelsizer = wx.BoxSizer(wx.VERTICAL)
        sizer_panelsizer.AddStretchSpacer(1)
        sizer_panelsizer.Add(sizer_panelcombo, 0, wx.ALL|wx.EXPAND, 2)
        sizer_panelsizer.Add(sizer_panelcombo2, 0, wx.ALL|wx.EXPAND, 2)
        sizer_panelsizer.AddStretchSpacer(1)
        sizer_panel.SetSizer(sizer_panelsizer)


        # This is new page

        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self._bitmap_creation_dc.SetFont(label_font)

         # This is new page


        scheme = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Appearance", CreateBitmap("eye"))
        self._default_primary, self._default_secondary, self._default_tertiary = self._ribbon.GetArtProvider().GetColourScheme(1, 1, 1)


        # This is new panel art

        provider_panel = RB.RibbonPanel(scheme, wx.ID_ANY, "", wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                        agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
        provider_bar = RB.RibbonButtonBar(provider_panel, wx.ID_ANY)
        provider_bar.AddSimpleButton(ID_DEFAULT_PROVIDER, "Default Provider",
                                     wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, wx.Size(32, 32)), "")
        provider_bar.AddSimpleButton(ID_AUI_PROVIDER, "AUI Provider", CreateBitmap("aui_style"), "")
        provider_bar.AddSimpleButton(ID_MSW_PROVIDER, "MSW Provider", CreateBitmap("msw_style"), "")



        # This is new panel primary colour
        primary_panel = RB.RibbonPanel(scheme, wx.ID_ANY, "", CreateBitmap("colours"))
        self._primary_gallery = self.PopulateColoursPanel(primary_panel, self._default_primary, ID_PRIMARY_COLOUR)



        # This is new panel secondary colour
        secondary_panel = RB.RibbonPanel(scheme, wx.ID_ANY, "", CreateBitmap("colours"))
        self._secondary_gallery = self.PopulateColoursPanel(secondary_panel, self._default_secondary, ID_SECONDARY_COLOUR)




        # This is new panel empty page

        dummy_2 = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Empty Page", CreateBitmap("empty"))
        dummy_3 = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Another Page", CreateBitmap("empty"))

        # Noew Realize all of them
        self._ribbon.Realize()

        # This main screen with text box, we defined the size
        # Now its not on the screeen. But we will use it late.
        # self._logwindow = wx.TextCtrl(panel, wx.ID_ANY, "", wx.DefaultPosition, size=(210, 20), style=wx.SUNKEN_BORDER)


        # We added NotebookDemo for lef t side screen, testauipanel for design screen, testsearchcontrol for search buton
        self.notebook = NotebookDemo(panel)
        self.panel2 = TestAuiPanel(panel)
        # self.search_button = TestSearchCtrl(panel)
        self.search = TestSearchCtrl(panel)

        # tb.AddControl(search)
        # We make a sizer here and then assign proportion
        # We added 3 more sizers. In s2 there are s2a and s2b

        s = wx.BoxSizer(wx.VERTICAL)
        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2a = wx.BoxSizer(wx.VERTICAL)
        s2b = wx.BoxSizer(wx.VERTICAL)

        # We added s2 sizer in s and other sizer in s2
        s.Add(self._ribbon, 1, wx.EXPAND)
        s.Add(s2, 6, wx.EXPAND)
        s2.Add(s2a, 1, wx.EXPAND)
        s2.Add(s2b, 6, wx.EXPAND)

        # logwindow yerine Demo'dan Toolbar orneginden al
        s2b.Add(self.panel2, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.notebook, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.search, 0, wx.EXPAND | wx.FIXED_MINSIZE)

        panel.SetSizer(s)
        self.panel = panel

        self.BindEvents([selection, shapes, provider_bar, toolbar_panel])
        self.SetIcon(images.Mondrian.Icon)
        self.CenterOnScreen()
        self.Show()


    def BindEvents(self, bars):

        selection, shapes, provider_bar, toolbar_panel = bars

        provider_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnDefaultProvider, id=ID_DEFAULT_PROVIDER)
        provider_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAUIProvider, id=ID_AUI_PROVIDER)
        provider_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnMSWProvider, id=ID_MSW_PROVIDER)
        selection.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSelectionExpandHButton, id=ID_SELECTION_EXPAND_H)
        selection.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSelectionExpandVButton, id=ID_SELECTION_EXPAND_V)
        selection.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSelectionContractButton, id=ID_SELECTION_CONTRACT)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnCircleButton, id=ID_CIRCLE)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnCrossButton, id=ID_CROSS)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnTriangleButton, id=ID_TRIANGLE)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSquareButton, id=ID_SQUARE)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED, self.OnTriangleDropdown, id=ID_TRIANGLE)
        shapes.Bind(RB.EVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED, self.OnPolygonDropdown, id=ID_POLYGON)
        toolbar_panel.Bind(RB.EVT_RIBBONPANEL_EXTBUTTON_ACTIVATED, self.OnExtButton)

        self.Bind(RB.EVT_RIBBONGALLERY_HOVER_CHANGED, self.OnHoveredColourChange, id=ID_PRIMARY_COLOUR)
        self.Bind(RB.EVT_RIBBONGALLERY_HOVER_CHANGED, self.OnHoveredColourChange, id=ID_SECONDARY_COLOUR)
        self.Bind(RB.EVT_RIBBONGALLERY_SELECTED, self.OnPrimaryColourSelect, id=ID_PRIMARY_COLOUR)
        self.Bind(RB.EVT_RIBBONGALLERY_SELECTED, self.OnSecondaryColourSelect, id=ID_SECONDARY_COLOUR)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnNew, id=wx.ID_NEW)
        self.Bind(RB.EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, self.OnNewDropdown, id=wx.ID_NEW)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnPrint, id=wx.ID_PRINT)
        self.Bind(RB.EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, self.OnPrintDropdown, id=wx.ID_PRINT)
        self.Bind(RB.EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, self.OnRedoDropdown, id=wx.ID_REDO)
        self.Bind(RB.EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, self.OnUndoDropdown, id=wx.ID_UNDO)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnPositionLeft, id=ID_POSITION_LEFT)
        self.Bind(RB.EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, self.OnPositionLeftDropdown, id=ID_POSITION_LEFT)
        self.Bind(RB.EVT_RIBBONTOOLBAR_CLICKED, self.OnPositionTop, id=ID_POSITION_TOP)
        self.Bind(wx.EVT_BUTTON, self.OnColourGalleryButton, id=ID_PRIMARY_COLOUR)
        self.Bind(wx.EVT_BUTTON, self.OnColourGalleryButton, id=ID_SECONDARY_COLOUR)
        self.Bind(wx.EVT_MENU, self.OnPositionLeftIcons, id=ID_POSITION_LEFT)
        self.Bind(wx.EVT_MENU, self.OnPositionLeftLabels, id=ID_POSITION_LEFT_LABELS)
        self.Bind(wx.EVT_MENU, self.OnPositionLeftBoth, id=ID_POSITION_LEFT_BOTH)
        self.Bind(wx.EVT_MENU, self.OnPositionTopLabels, id=ID_POSITION_TOP)
        self.Bind(wx.EVT_MENU, self.OnPositionTopIcons, id=ID_POSITION_TOP_ICONS)
        self.Bind(wx.EVT_MENU, self.OnPositionTopBoth, id=ID_POSITION_TOP_BOTH)



    def SetBarStyle(self, agwStyle):

        self._ribbon.Freeze()
        self._ribbon.SetAGWWindowStyleFlag(agwStyle)

        pTopSize = self.panel.GetSizer()
        pToolbar = wx.FindWindowById(ID_MAIN_TOOLBAR)

        if agwStyle & RB.RIBBON_BAR_FLOW_VERTICAL:

            self._ribbon.SetTabCtrlMargins(10, 10)
            pTopSize.SetOrientation(wx.HORIZONTAL)
            if pToolbar:
                pToolbar.SetRows(3, 5)

        else:

            self._ribbon.SetTabCtrlMargins(50, 20)
            pTopSize.SetOrientation(wx.VERTICAL)
            if pToolbar:
                pToolbar.SetRows(2, 3)

        self._ribbon.Realize()
        self._ribbon.Thaw()
        self.panel.Layout()


    def PopulateColoursPanel(self, panel, defc, gallery_id):

        gallery = wx.FindWindowById(gallery_id, panel)

        if gallery:
            gallery.Clear()
        else:
            gallery = RB.RibbonGallery(panel, gallery_id)

        dc = self._bitmap_creation_dc
        def_item = self.AddColourToGallery(gallery, "Default", dc, defc)
        gallery.SetSelection(def_item)

        self.AddColourToGallery(gallery, "BLUE", dc)
        self.AddColourToGallery(gallery, "BLUE VIOLET", dc)
        self.AddColourToGallery(gallery, "BROWN", dc)
        self.AddColourToGallery(gallery, "CADET BLUE", dc)
        self.AddColourToGallery(gallery, "CORAL", dc)
        self.AddColourToGallery(gallery, "CYAN", dc)
        self.AddColourToGallery(gallery, "DARK GREEN", dc)
        self.AddColourToGallery(gallery, "DARK ORCHID", dc)
        self.AddColourToGallery(gallery, "FIREBRICK", dc)
        self.AddColourToGallery(gallery, "GOLD", dc)
        self.AddColourToGallery(gallery, "GOLDENROD", dc)
        self.AddColourToGallery(gallery, "GREEN", dc)
        self.AddColourToGallery(gallery, "INDIAN RED", dc)
        self.AddColourToGallery(gallery, "KHAKI", dc)
        self.AddColourToGallery(gallery, "LIGHT BLUE", dc)
        self.AddColourToGallery(gallery, "LIME GREEN", dc)
        self.AddColourToGallery(gallery, "MAGENTA", dc)
        self.AddColourToGallery(gallery, "MAROON", dc)
        self.AddColourToGallery(gallery, "NAVY", dc)
        self.AddColourToGallery(gallery, "ORANGE", dc)
        self.AddColourToGallery(gallery, "ORCHID", dc)
        self.AddColourToGallery(gallery, "PINK", dc)
        self.AddColourToGallery(gallery, "PLUM", dc)
        self.AddColourToGallery(gallery, "PURPLE", dc)
        self.AddColourToGallery(gallery, "RED", dc)
        self.AddColourToGallery(gallery, "SALMON", dc)
        self.AddColourToGallery(gallery, "SEA GREEN", dc)
        self.AddColourToGallery(gallery, "SIENNA", dc)
        self.AddColourToGallery(gallery, "SKY BLUE", dc)
        self.AddColourToGallery(gallery, "TAN", dc)
        self.AddColourToGallery(gallery, "THISTLE", dc)
        self.AddColourToGallery(gallery, "TURQUOISE", dc)
        self.AddColourToGallery(gallery, "VIOLET", dc)
        self.AddColourToGallery(gallery, "VIOLET RED", dc)
        self.AddColourToGallery(gallery, "WHEAT", dc)
        self.AddColourToGallery(gallery, "WHITE", dc)
        self.AddColourToGallery(gallery, "YELLOW", dc)

        return gallery


    def GetGalleryColour(self, gallery, item, name=None):

        data = gallery.GetItemClientData(item)

        if name != None:
            name = data.GetName()

        return data.GetColour(), name


    def OnHoveredColourChange(self, event):

        # Set the background of the gallery to the hovered colour, or back to the
        # default if there is no longer a hovered item.

        gallery = event.GetGallery()
        provider = gallery.GetArtProvider()

        if event.GetGalleryItem() != None:
            if provider == self._ribbon.GetArtProvider():
                provider = provider.Clone()
                gallery.SetArtProvider(provider)

            provider.SetColour(RB.RIBBON_ART_GALLERY_HOVER_BACKGROUND_COLOUR,
                               self.GetGalleryColour(event.GetGallery(), event.GetGalleryItem(), None)[0])

        else:
            if provider != self._ribbon.GetArtProvider():
                gallery.SetArtProvider(self._ribbon.GetArtProvider())
                del provider


    def OnPrimaryColourSelect(self, event):

        colour, name = self.GetGalleryColour(event.GetGallery(), event.GetGalleryItem(), "")
        self.AddText("Colour %s selected as primary."%name)

        dummy, secondary, tertiary = self._ribbon.GetArtProvider().GetColourScheme(None, 1, 1)
        self._ribbon.GetArtProvider().SetColourScheme(colour, secondary, tertiary)
        self.ResetGalleryArtProviders()
        self._ribbon.Refresh()


    def OnSecondaryColourSelect(self, event):

        colour, name = self.GetGalleryColour(event.GetGallery(), event.GetGalleryItem(), "")
        self.AddText("Colour %s selected as secondary."%name)

        primary, dummy, tertiary = self._ribbon.GetArtProvider().GetColourScheme(1, None, 1)
        self._ribbon.GetArtProvider().SetColourScheme(primary, colour, tertiary)
        self.ResetGalleryArtProviders()
        self._ribbon.Refresh()


    def ResetGalleryArtProviders(self):

        if self._primary_gallery.GetArtProvider() != self._ribbon.GetArtProvider():
            self._primary_gallery.SetArtProvider(self._ribbon.GetArtProvider())

        if self._secondary_gallery.GetArtProvider() != self._ribbon.GetArtProvider():
            self._secondary_gallery.SetArtProvider(self._ribbon.GetArtProvider())


    def OnSelectionExpandHButton(self, event):

        self.AddText("Expand selection horizontally button clicked.")


    def OnSelectionExpandVButton(self, event):

        self.AddText("Expand selection vertically button clicked.")


    def OnSelectionContractButton(self, event):

        self.AddText("Contract selection button clicked.")


    def OnCircleButton(self, event):

        self.AddText("Circle button clicked.")


    def OnCrossButton(self, event):

        self.AddText("Cross button clicked.")


    def OnTriangleButton(self, event):

        self.AddText("Triangle button clicked.")


    def OnTriangleDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Equilateral")
        menu.Append(wx.ID_ANY, "Isosceles")
        menu.Append(wx.ID_ANY, "Scalene")

        event.PopupMenu(menu)


    def OnSquareButton(self, event):

        self.AddText("Square button clicked.")


    def OnPolygonDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Pentagon (5 sided)")
        menu.Append(wx.ID_ANY, "Hexagon (6 sided)")
        menu.Append(wx.ID_ANY, "Heptagon (7 sided)")
        menu.Append(wx.ID_ANY, "Octogon (8 sided)")
        menu.Append(wx.ID_ANY, "Nonagon (9 sided)")
        menu.Append(wx.ID_ANY, "Decagon (10 sided)")

        event.PopupMenu(menu)


    def OnNew(self, event):

        self.AddText("New button clicked.")


    def OnNewDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "New Document")
        menu.Append(wx.ID_ANY, "New Template")
        menu.Append(wx.ID_ANY, "New Mail")

        event.PopupMenu(menu)


    def OnPrint(self, event):

        self.AddText("Print button clicked.")


    def OnPrintDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Print")
        menu.Append(wx.ID_ANY, "Preview")
        menu.Append(wx.ID_ANY, "Options")

        event.PopupMenu(menu)


    def OnRedoDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Redo E")
        menu.Append(wx.ID_ANY, "Redo F")
        menu.Append(wx.ID_ANY, "Redo G")

        event.PopupMenu(menu)


    def OnUndoDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Undo C")
        menu.Append(wx.ID_ANY, "Undo B")
        menu.Append(wx.ID_ANY, "Undo A")

        event.PopupMenu(menu)


    def OnPositionTopLabels(self, event):

        self.SetBarStyle(RB.RIBBON_BAR_DEFAULT_STYLE)


    def OnPositionTopIcons(self, event):

        self.SetBarStyle((RB.RIBBON_BAR_DEFAULT_STYLE &~RB.RIBBON_BAR_SHOW_PAGE_LABELS)
                         | RB.RIBBON_BAR_SHOW_PAGE_ICONS)


    def OnPositionTopBoth(self, event):

        self.SetBarStyle(RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PAGE_ICONS)


    def OnPositionLeftLabels(self, event):

        self.SetBarStyle(RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_FLOW_VERTICAL)


    def OnPositionLeftIcons(self, event):

        self.SetBarStyle((RB.RIBBON_BAR_DEFAULT_STYLE &~RB.RIBBON_BAR_SHOW_PAGE_LABELS) |
                         RB.RIBBON_BAR_SHOW_PAGE_ICONS | RB.RIBBON_BAR_FLOW_VERTICAL)


    def OnPositionLeftBoth(self, event):

        self.SetBarStyle(RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PAGE_ICONS |
                         RB.RIBBON_BAR_FLOW_VERTICAL)


    def OnPositionTop(self, event):

        self.OnPositionTopLabels(event)


    def OnPositionTopDropdown(self, event):

        menu = wx.Menu()
        menu.Append(ID_POSITION_TOP, "Top with Labels")
        menu.Append(ID_POSITION_TOP_ICONS, "Top with Icons")
        menu.Append(ID_POSITION_TOP_BOTH, "Top with Both")
        event.PopupMenu(menu)


    def OnPositionLeft(self, event):

        self.OnPositionLeftIcons(event)


    def OnPositionLeftDropdown(self, event):

        menu = wx.Menu()
        menu.Append(ID_POSITION_LEFT, "Left with Icons")
        menu.Append(ID_POSITION_LEFT_LABELS, "Left with Labels")
        menu.Append(ID_POSITION_LEFT_BOTH, "Left with Both")
        event.PopupMenu(menu)


    def OnTogglePanels(self, event):

        self._ribbon.ShowPanels(self._togglePanels.GetValue())


    def OnExtButton(self, event):

        wx.MessageBox("Extended button activated")


    def AddText(self, msg):

        self._logwindow.AppendText(msg)
        self._logwindow.AppendText("\n")
        self._ribbon.DismissExpandedPanel()


    def AddColourToGallery(self, gallery, colour, dc, value=None):

        item = None

        if colour != "Default":
            c = wx.NamedColour(colour)

        if value is not None:
            c = value

        if c.IsOk():

            iWidth = 64
            iHeight = 40

            bitmap = wx.EmptyBitmap(iWidth, iHeight)
            dc.SelectObject(bitmap)
            b = wx.Brush(c)
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(b)
            dc.DrawRectangle(0, 0, iWidth, iHeight)

            colour = colour[0] + colour[1:].lower()
            size = wx.Size(*dc.GetTextExtent(colour))
            notcred = min(abs(~c.Red()), 255)
            notcgreen = min(abs(~c.Green()), 255)
            notcblue = min(abs(~c.Blue()), 255)

            foreground = wx.Colour(notcred, notcgreen, notcblue)

            if abs(foreground.Red() - c.Red()) + abs(foreground.Blue() - c.Blue()) + abs(foreground.Green() - c.Green()) < 64:
                # Foreground too similar to background - use a different
                # strategy to find a contrasting colour
                foreground = wx.Colour((c.Red() + 64) % 256, 255 - c.Green(),
                                       (c.Blue() + 192) % 256)

            dc.SetTextForeground(foreground)
            dc.DrawText(colour, (iWidth - size.GetWidth() + 1) / 2, (iHeight - size.GetHeight()) / 2)
            dc.SelectObjectAsSource(wx.NullBitmap)

            item = gallery.Append(bitmap, wx.ID_ANY)
            gallery.SetItemClientData(item, ColourClientData(colour, c))

        return item


    def OnColourGalleryButton(self, event):

        gallery = event.GetEventObject()
        if gallery is None:
            return

        self._ribbon.DismissExpandedPanel()
        if gallery.GetSelection():
            self._colour_data.SetColour(self.GetGalleryColour(gallery, gallery.GetSelection(), None)[0])

        dlg = wx.ColourDialog(self, self._colour_data)

        if dlg.ShowModal() == wx.ID_OK:

            self._colour_data = dlg.GetColourData()
            clr = self._colour_data.GetColour()

            # Try to find colour in gallery
            item = None
            for i in xrange(gallery.GetCount()):
                item = gallery.GetItem(i)
                if self.GetGalleryColour(gallery, item, None)[0] == clr:
                    break
                else:
                    item = None

            # Colour not in gallery - add it
            if item == None:
                item = self.AddColourToGallery(gallery, clr.GetAsString(wx.C2S_HTML_SYNTAX), self._bitmap_creation_dc,
                                               clr)
                gallery.Realize()

            # Set selection
            gallery.EnsureVisible(item)
            gallery.SetSelection(item)

            # Send an event to respond to the selection change
            dummy = RB.RibbonGalleryEvent(RB.wxEVT_COMMAND_RIBBONGALLERY_SELECTED, gallery.GetId())
            dummy.SetEventObject(gallery)
            dummy.SetGallery(gallery)
            dummy.SetGalleryItem(item)
            self.GetEventHandler().ProcessEvent(dummy)


    def OnDefaultProvider(self, event):

        self._ribbon.DismissExpandedPanel()
        self.SetArtProvider(RB.RibbonDefaultArtProvider())


    def OnAUIProvider(self, event):

        self._ribbon.DismissExpandedPanel()
        self.SetArtProvider(RB.RibbonAUIArtProvider())


    def OnMSWProvider(self, event):

        self._ribbon.DismissExpandedPanel()
        self.SetArtProvider(RB.RibbonMSWArtProvider())


    def SetArtProvider(self, prov):

        self._ribbon.Freeze()
        self._ribbon.SetArtProvider(prov)

        self._default_primary, self._default_secondary, self._default_tertiary = \
                               prov.GetColourScheme(self._default_primary, self._default_secondary, self._default_tertiary)
        self.PopulateColoursPanel(self._primary_gallery.GetParent(), self._default_primary,
                                  ID_PRIMARY_COLOUR)
        self.PopulateColoursPanel(self._secondary_gallery.GetParent(), self._default_secondary,
                                  ID_SECONDARY_COLOUR)

        self._ribbon.Thaw()
        self.panel.GetSizer().Layout()
        self._ribbon.Realize()




if __name__ == '__main__':
    app = wx.App()
    frame = RibbonFrame(None, -1, "wxPython Ribbon Sample Application",size=(900, 800))
    frame.Show(True)
    frame.Centre()
    app.MainLoop()

