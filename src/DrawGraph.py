'''
        This is PypeGraph.py
        PypeGraph uses the Graph structure defined in Pypeline.py
        an wxPython/FloatCanvas to create a drawing
        surface for creating a pipeline network model

        further more it defines drawing utilies for
        a graphically representing a graph

        ##contracts
'''
import wx
import numpy as N
from wx.lib.floatcanvas import NavCanvas, FloatCanvas
import Pypeline as PL


'''Global variables'''

GRAPH_HEIGHT = 640
GRAPH_WIDTH = 800
GRAPH_SIZE = (GRAPH_WIDTH, GRAPH_HEIGHT)
NODE_SIZE = 10


class DrawingGraph(PL.Graph):
    def __init__(self):
            PL.Graph.__init__(self)

    ##this uses BFT(breadth first traversal) to draw every node and
    ##edge in the graph
    def draw(self,Canvas):
        for node in self.nodes:
            Canvas.AddCircle(
                node.pos,
                10,
                LineWidth=1,
                LineColor='BLACK',
                FillColor='BLACK'
            )
            for edge in node._neighbors:
                line = (node.pos, edge.node.pos)
                Canvas.AddArrowLine(
                    line, LineWidth=2,
                    LineColor="RED",
                    ArrowHeadSize=16
                )
