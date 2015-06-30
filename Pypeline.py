from __future__ import division
import wx
import time
import os
import sys
import images
import wx.aui
import wx.lib.agw.ribbon as RB
from wx.lib.floatcanvas import Resources
import GraphDesignPanel as  GDP
import PypeGraph as PypeGraph
import NodeTabPanel, PipeTabPanel, ValveTabPanel, CompressorTabPanel, RegulatorTabPanel, LossElementTabPanel
import wx.lib.agw.gradientbutton as GB

'''EXCEPTION TESTING'''

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])


########################################################################

def CreateBitmap(xpm):

    bmp = eval(xpm).Bitmap

    return bmp

def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result

##SOME ID CONSTANTS FOR DESIGN BUTTONS

ID_NODES = wx.ID_HIGHEST + 1
ID_VALVES = ID_NODES + 1
ID_COMPRESSORS = ID_NODES + 2
ID_REGULATORS = ID_NODES + 3
ID_LOSS_ELEMENTS = ID_NODES + 4
ID_ZOOM_IN = ID_NODES + 5
ID_ZOOM_OUT = ID_NODES + 6
ID_PAN = ID_NODES + 7
ID_TOGGLE_MAP = ID_NODES + 8
ID_SELECT_NODES = ID_NODES + 9
ID_SELECT_PIPES = ID_NODES + 10
ID_DELETE_NODE = ID_NODES + 11
ID_UNDO = ID_NODES + 12
ID_REDO = ID_NODES + 13

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


'''Static Text with no Background color'''

class TransparentText(wx.StaticText):
  def __init__(self, parent, id=wx.ID_ANY, label='',
               pos=wx.DefaultPosition, size=wx.DefaultSize,
               style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
    wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

    self.Bind(wx.EVT_PAINT, self.on_paint)
    self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
    self.Bind(wx.EVT_SIZE, self.on_size)

  def on_paint(self, event):
    bdc = wx.PaintDC(self)
    dc = wx.GCDC(bdc)

    font_face = self.GetFont()
    font_color = self.GetForegroundColour()

    dc.SetFont(font_face)
    dc.SetTextForeground(font_color)
    dc.DrawText(self.GetLabel(), 0, 0)

  def on_size(self, event):
    self.Refresh()
    event.Skip()

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

'''STATUS BAR SECTION'''
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


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

'''SEARCH BAR'''


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


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


'''LEFT HAND SIDE ELEMENT CONTROL NOTEBOOK'''

class Notebook(wx.Notebook):
    """
        Notebook class
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, size=(278, 30), style=
                             wx.BK_TOP
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )


        # HOW TO PUT IMAGES ON NOTEBOOK TABS
        # first make the image list:
        # il = wx.ImageList(16, 16)
        # idx1 = il.Add(images.Smiles.GetBitmap())
        # self.AssignImageList(il)
        #
        # self.SetPageImage(0, idx1)

        # ADD NOTEBOOK PAGES
        self.AddPage(NodeTabPanel.NodeTabPanel(self), "ND")
        self.AddPage(PipeTabPanel.PipeTabPanel(self), "PP")
        self.AddPage(ValveTabPanel.ValveTabPanel(self), "VV")
        self.AddPage(CompressorTabPanel.CompressorTabPanel(self), "CP")
        self.AddPage(RegulatorTabPanel.RegulatorTabPanel(self), "RG")
        self.AddPage(LossElementTabPanel.LossElementTabPanel(self), "LE")

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

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

'''wxRIBBON INITIALIZATION'''

class RibbonFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # CHANGE WHEN WE LEARN HOW TO USE TOP LEFT CORNER OF RIBBON TOOLBAR
        # b = wx.Button(self, wx.ID_ANY, "Default Button", pos=(1, 1), size = (20, 20))

        menubar = wx.MenuBar()
        # CATEGORIES WITHIN FILE SHOULD BE SEPARATED ACCORDING TO FUNCTION
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, '&New')
        fileMenu.Append(wx.ID_OPEN, '&Open')

        fileMenu.AppendSeparator()

        fileMenu.Append(wx.ID_SAVE, '&Save')
        fileMenu.Append(wx.ID_SAVE, '&Save As')

        fileMenu.AppendSeparator()

        fileMenu.Append(wx.ID_ANY, 'Import')
        fileMenu.Append(wx.ID_ANY, 'Export')

        fileMenu.AppendSeparator()

        fileMenu.Append(wx.ID_ANY, 'Screenshot')

        quit_menu_item = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+W')

        fileMenu.AppendSeparator()

        fileMenu.AppendItem(quit_menu_item)


        self.Bind(wx.EVT_MENU, self.OnQuit, quit_menu_item)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

        panel = wx.Panel(self)


        # TRYING TO ADD DROPDOWN MENU TO FIRST PANEL
        # http://wxpython.org/Phoenix/docs/html/lib.agw.ribbon.panel.RibbonPanel.html
        # RIBBON_PANEL_EXT_BUTTON

        self._ribbon = RB.RibbonBar(panel, wx.ID_ANY, agwStyle=RB.RIBBON_BAR_DEFAULT_STYLE|RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)
        self._bitmap_creation_dc = wx.MemoryDC()
        self._colour_data = wx.ColourData()


        '''RIBBON PAGES'''
        File = RB.RibbonPage(self._ribbon, wx.ID_ANY, "FILE")
        Options = RB.RibbonPage(self._ribbon, wx.ID_ANY, "OPTIONS")
        Mapping = RB.RibbonPage(self._ribbon, wx.ID_ANY, "MAPPING")
        Design = RB.RibbonPage(self._ribbon, wx.ID_ANY, "DESIGN")
        Simulation_Settings = RB.RibbonPage(self._ribbon, wx.ID_ANY, "SIMULATION SETTINGS")
        Results = RB.RibbonPage(self._ribbon, wx.ID_ANY, "RESULTS")
        Help = RB.RibbonPage(self._ribbon, wx.ID_ANY, "HELP")


        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''FILE PAGE'''

        # REALLY NEED TO CHANGE THE NAME FROM TOOLBAR TO FILE OR WHATEVER NAME WE'RE USING


        toolbar_panel = RB.RibbonPanel(File, wx.ID_ANY, "", wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE|RB.RIBBON_PANEL_EXT_BUTTON)

        # THE TOOLBAR WITHIN RIBBON MEANS A GRID LIKE PANEL
        toolbar = RB.RibbonToolBar(toolbar_panel, wx.ID_ANY)

        toolbar.AddSeparator()
        toolbar.AddHybridTool(wx.ID_NEW, wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_OTHER, wx.Size(24, 24)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, wx.Size(24, 23)))

        toolbar.AddSeparator()
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, wx.Size(24, 23)))

        toolbar.AddSeparator()
        toolbar.AddHybridTool(wx.ID_PRINT, wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_OTHER, wx.Size(24, 23)),
                              "Print button")
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_OTHER, wx.Size(24, 23)))

        toolbar.AddSeparator()
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_OTHER, wx.Size(24, 23)))
        toolbar.AddTool(wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_OTHER, wx.Size(24, 23)))

        toolbar.SetRows(2, 3)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''OPTIONS PAGE'''

        # OPTIONS PAGE'S PANELS
        Options_Settings = RB.RibbonPanel(Options, wx.ID_ANY, "Settings", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Options_Window_Options = RB.RibbonPanel(Options, wx.ID_ANY, "Window Options", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN OPTIONS PAGE
        Settings_Group = RB.RibbonButtonBar(Options_Settings)
        Windows_options_Group = RB.RibbonButtonBar(Options_Window_Options)

        # BUTTON ICONS
        # CHANGE CHANGE CHANGE
        options_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp5 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp6 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp7 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp8 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp9 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp10 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp11 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp12 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp13 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # BUTTONS
        # Testen Sie the toggle :)
        # AddToggleButton(self, button_id, label, bitmap, help_string="")

        Settings_Group.AddSimpleButton(wx.ID_ANY, "General Settings", options_bmp1,
                                  "This is a tooltip for adding Nodes")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Display / Labeling Settings", options_bmp2,
                                  "This is a tooltip for adding Valves")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Unit Settings", options_bmp3,
                                  "This is a tooltip for adding Compressors")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Short-Cut Settings", options_bmp4,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Mapping On", options_bmp5,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Labels On", options_bmp6,
                                  "This is a tooltip for adding Nodes")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Grid On", options_bmp7,
                                  "This is a tooltip for adding Valves")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Scale On", options_bmp8,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Element Screen On", options_bmp9,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Outline Screen  On", options_bmp10,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Calculator On", options_bmp11,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Isometric View On", options_bmp12,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "3D Screen On", options_bmp13,
                                  "This is a tooltip for adding Loss Elements")

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''MAPPING PAGE'''

        # PAGE'S PANELS
        Mapping_Panel = RB.RibbonPanel(Mapping, wx.ID_ANY, "Background/Image", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _GIS = RB.RibbonPanel(Mapping, wx.ID_ANY, "GIS", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL
        Images_Group = RB.RibbonButtonBar(Mapping_Panel)
        GIS_Group = RB.RibbonButtonBar(_GIS)

        # BUTTON ICONS
        # CHANGE CHANGE CHANGE
        options_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()


        # BUTTONS
        # Testen Sie the toggle :)
        # AddToggleButton(self, button_id, label, bitmap, help_string="")

        Images_Group.AddSimpleButton(wx.ID_ANY, "Change Background Color", options_bmp1,
                                  "This is a tooltip for adding Nodes")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Import/ Change Image", options_bmp2,
                                  "This is a tooltip for adding Valves")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Delete Image", options_bmp3,
                                  "This is a tooltip for adding Compressors")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Image Settings", options_bmp4,
                                  "This is a tooltip for adding Regulators")

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''DESIGN PAGE'''

        # ICONS FOR DESIGN PAGE (MOVE TO GENERAL ICON SECTION LATER)
        # ICONS FOR FIRST PANEL IN DESIGN PAGE
        # VIEWING ICONS ARE TAKEN FROM FLOATCANVAS RESOURCES TO BE REPLACED BY OTHER ICONS LATER

        # ICONS for drawing_tools
        # PLEASE CHANGE ALL BMP ICON NAMES TO REFLECT RELATIVE PANEL
        bmp1= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp2= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp3= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp4= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp5= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # ICONS for viewing_tools
        bmp6= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp7= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # ICONS for general tools
        bmp8 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp9 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp10 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp11 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp12 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp13 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp14 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # PANELS IN DESIGN RIBBON PAGE
        _Element_Add = RB.RibbonPanel(Design, wx.ID_ANY, "Add Element", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_General = RB.RibbonPanel(Design, wx.ID_ANY, "Design General", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_View = RB.RibbonPanel(Design, wx.ID_ANY, "Design View", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Element_Control = RB.RibbonPanel(Design, wx.ID_ANY, "Element Control", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Coordinate_Control = RB.RibbonPanel(Design, wx.ID_ANY, "Coordinate Control", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN DESIGN PAGE
        drawing_tools = RB.RibbonButtonBar(_Element_Add)
        viewing_tools = RB.RibbonButtonBar(_Design_View)
        general_tools = RB.RibbonButtonBar(_Design_General)
        element_tools = RB.RibbonButtonBar(_Element_Control)

        ##MAKE THE BUTTONS
        drawing_tools.AddToggleButton(ID_NODES, "Nodes", bmp1,
                                  "This is a tooltip for adding Nodes")
        drawing_tools.AddToggleButton(ID_NODES, "Pipes", bmp2,
                                  "This is a tooltip for adding Pipes")
        drawing_tools.AddToggleButton(ID_VALVES, "Valves", bmp3,
                                  "This is a tooltip for adding Valves")
        drawing_tools.AddToggleButton(ID_COMPRESSORS, "Compressors", bmp4,
                                  "This is a tooltip for adding Compressors")
        drawing_tools.AddToggleButton(ID_REGULATORS, "Regulators", bmp5,
                                  "This is a tooltip for adding Regulators")
        drawing_tools.AddToggleButton(ID_LOSS_ELEMENTS, "Loss", bmp6,
                                  "This is a tooltip for adding Loss Elements")


        viewing_tools.AddToggleButton(ID_ZOOM_IN, "Zoom In", Resources.getMagPlusBitmap(),
                                  "This is a tooltip for zooming")
        viewing_tools.AddToggleButton(ID_ZOOM_OUT, "Zoom Out", Resources.getMagMinusBitmap(),
                                  "This is a tooltip for zooming out")
        viewing_tools.AddToggleButton(ID_PAN, "Panning", Resources.getHandBitmap(),
                                  "This is a tooltip for panning")

        general_tools.AddToggleButton(ID_SELECT_NODES, "Node Select", bmp8,
                                  "This is a tooltip for selecting")
        general_tools.AddToggleButton(ID_SELECT_PIPES, "Pipe select", bmp9,
                                  "This is a tooltip for selecting")
        general_tools.AddToggleButton(ID_DELETE_NODE, "Delete", bmp10,
                                  "This is a tooltip for deleting elements")
        general_tools.AddToggleButton(ID_UNDO, "Undo", bmp11,
                                  "This is a tooltip to undo")
        general_tools.AddToggleButton(ID_REDO, "Redo", bmp12,
                                  "This is a tooltip to redo")

        element_tools.AddSimpleButton(wx.ID_ANY, "Properties", bmp13,
                                  "This is a tooltip to change element properties")

        # SIZER FOR COORDINATES PANEL
        coord_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # CONTROLS FOR COORDINATES PANEL
        coord_t1 = wx.TextCtrl(_Coordinate_Control, -1, "", size=(80, -1))
        coord_button_1 = GB.GradientButton(_Coordinate_Control, -1, None, "Coordinate", (100, 50), size=(80, 40))
        # coord_button_1.SetTopStartColour('BLACK')
        # coord_button_1.SetTopEndColour('RED')
        # coord_button_1.SetBottomStartColour('RED')
        # coord_button_1.SetBottomEndColour('BLACK')

        # ADD CONTROLS TO SIZER
        coord_sizer.Add(coord_t1, 1, wx.TOP|wx.RIGHT|wx.LEFT, 10)
        coord_sizer.Add(coord_button_1, 1, wx.TOP|wx.RIGHT, 10)

        # SET SIZER FOR _Coordinate_Control
        _Coordinate_Control.SetSizer(coord_sizer)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''SIMULATION SETTINGS PAGE'''

        # PANELS AND BUTTONS BARS
        Sim_Panel1 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel2 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "General",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel3 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Details",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel4 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Optimization",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        # Sim_Panel5 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation",
        #                              wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
        #                              agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        # Sim_Panel6 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation check and run",
        #                              wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
        #                              agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel7 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Check and Run",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel8 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Success",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)

        Sim_Bar1 = RB.RibbonButtonBar(Sim_Panel2)
        Sim_Bar2 = RB.RibbonButtonBar(Sim_Panel4)

        # ICONS
        sim_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp5 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # CONTROLS FOR PANEL 1
        simulation_choices1 = ["Simulation 1", "Simulation 2", "Simulation 3",
                                      "Simulation 4", "Simulation 5", "Simulation 6"]
        simulation_choices2 = ["Steady State", "Transient", "Steady State with Heat Transfer",]

        sim_cb1 = wx.ComboBox(Sim_Panel1, -1, "Choose Design to Simulate", (20,20),
                          (188, -1), simulation_choices1, wx.CB_DROPDOWN)
        sim_cb2 = wx.ComboBox(Sim_Panel1, -1, "Choose Method for Simulation", (20, 20),
                          (188, -1), simulation_choices2, wx.CB_DROPDOWN)

        # CONTROLS FOR PANEL 2
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "New Simulation Design", sim_bmp1,
                                  "Create and Name a new design in the drawing window")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Simulation Display Settings", sim_bmp2,
                                  "Colour range selection and labels for Design")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Design To Simulate", sim_bmp3,
                                  "Choose which design to simulate")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Fluid Properties", sim_bmp4,
                                  "Choose and edit fluid properties")

        Sim_Bar2.AddSimpleButton(wx.ID_ANY, "Optimization Window", sim_bmp4,
                                  "See possible Optimizations that can be made")

        # CONTROLS FOR PANEL 3
        sim_st1 = TransparentText(Sim_Panel3, -1, "Maximum Iteration")

        sim_st2 = TransparentText(Sim_Panel3, -1, "Convergence")

        sim_st2.SetBackgroundColour(wx.Colour(wx.TRANSPARENT))

        sim_st3 = TransparentText(Sim_Panel3, -1, "Tolerance")
        # sim_st3.SetBackgroundColour(wx.Colour(255, 251, 204))

        t1 = wx.TextCtrl(Sim_Panel3, -1, "", size=(80, -1))
        t2 = wx.TextCtrl(Sim_Panel3, -1, "", size=(80, -1))
        t3 = wx.TextCtrl(Sim_Panel3, -1, "", size=(80, -1))

        # CONTROLS FOR PANEL 7

        sim_run_button_1 = GB.GradientButton(Sim_Panel7, -1, None, "RUN", (100, 50), size=(150, -1))

        # sim_run_button_1.SetTopStartColour('WHITE')
        # sim_run_button_1.SetTopEndColour('BLUE')
        # sim_run_button_1.SetBottomStartColour('BLUE')
        # sim_run_button_1.SetBottomEndColour('WHITE')

        sim_run_button_2 = GB.GradientButton(Sim_Panel7, -1, None, "CHECK", (100, 50), size=(75, -1))

        # sim_run_button_2.SetTopStartColour('WHITE')
        # sim_run_button_2.SetTopEndColour('BLUE')
        # sim_run_button_2.SetBottomStartColour('BLUE')
        # sim_run_button_2.SetBottomEndColour('WHITE')

        sim_run_button_3 = GB.GradientButton(Sim_Panel7, -1, None, "INITIALIZE", (100, 50), size=(75, -1))

        # sim_run_button_3.SetTopStartColour('WHITE')
        # sim_run_button_3.SetTopEndColour('BLUE')
        # sim_run_button_3.SetBottomStartColour('BLUE')
        # sim_run_button_3.SetBottomEndColour('WHITE')

        # SetForegroundColour

         # CONTROLS FOR PANEL 8
        sim_st4 = TransparentText(Sim_Panel8, -1, "Simulation Status")
        sim_st5 = TransparentText(Sim_Panel8, -1, "Simulaion Errors")
        sim_st6 = TransparentText(Sim_Panel8, -1, "Convergence Time")
        sim_st7 = TransparentText(Sim_Panel8, -1, "Total Iteration")

        t4 = wx.TextCtrl(Sim_Panel8, -1, "", size=(80, -1))
        t5 = wx.TextCtrl(Sim_Panel8, -1, "", size=(80, -1))
        t6 = wx.TextCtrl(Sim_Panel8, -1, "", size=(80, -1))
        t7 = wx.TextCtrl(Sim_Panel8, -1, "", size=(80, -1))

        # SIZERS
        # SIZER FOR PANEL 1
        simulation_sizer1 = wx.BoxSizer(wx.VERTICAL)

        # SIZER FOR PANEL 2
        simulation_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer2.AddStretchSpacer(1)
        simulation_sizer3 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer3.AddStretchSpacer(1)
        simulation_sizer4 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer4.AddStretchSpacer(1)

        # SIZER FOR PANEL 7
        simulation_sizer_panel_7 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer_panel_7_2 = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer_panel_7_2.AddStretchSpacer(1)

        # SIZERS FOR PANEL 8
        simulation_sizer_panel_8 = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer_panel_8.AddStretchSpacer(1)
        simulation_sizer_panel_81 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer_panel_81.AddStretchSpacer(1)
        simulation_sizer_panel_82 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer_panel_82.AddStretchSpacer(1)
        simulation_sizer_panel_83 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer_panel_83.AddStretchSpacer(1)
        simulation_sizer_panel_84 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer_panel_84.AddStretchSpacer(1)

        # ADDING TO RESPECTIVE SIZERS
        # ADDING FOR PANEL 1
        simulation_sizer1.Add(sim_cb1, 0, wx.TOP, 15)
        simulation_sizer1.Add(sim_cb2, 0, wx.BOTTOM, 5)

        # ADDING FOR PANEL 2
        simulation_sizer2.Add(simulation_sizer3, 0, wx.TOP, 0)
        simulation_sizer2.Add(simulation_sizer4, 0, wx.TOP, 0)

        simulation_sizer3.Add(sim_st1, 0, wx.TOP, 3)
        simulation_sizer3.Add(sim_st2, 0, wx.TOP, 8)
        simulation_sizer3.Add(sim_st3, 0, wx.TOP, 8)

        simulation_sizer4.Add(t1, 0, wx.TOP, 0)
        simulation_sizer4.Add(t2, 0, wx.TOP, 0)
        simulation_sizer4.Add(t3, 0, wx.TOP, 0)

        # ADDING FOR PANEL 7
        simulation_sizer_panel_7.Add(sim_run_button_1, 0, wx.TOP|wx.RIGHT|wx.LEFT, 2)
        simulation_sizer_panel_7.Add(simulation_sizer_panel_7_2, 0, wx.TOP|wx.RIGHT|wx.LEFT, 2)

        simulation_sizer_panel_7_2.Add(sim_run_button_2, 0, wx.TOP|wx.RIGHT|wx.LEFT, 2)
        simulation_sizer_panel_7_2.Add(sim_run_button_3, 0, wx.TOP|wx.RIGHT|wx.LEFT, 2)


        # ADDING FOR PANEL 8
        simulation_sizer_panel_8.Add(simulation_sizer_panel_81, 0, wx.TOP, 0)
        simulation_sizer_panel_8.Add(simulation_sizer_panel_82, 0, wx.TOP, 0)
        simulation_sizer_panel_8.Add(simulation_sizer_panel_83, 0, wx.TOP, 0)
        simulation_sizer_panel_8.Add(simulation_sizer_panel_84, 0, wx.TOP, 0)

        simulation_sizer_panel_81.Add(sim_st4, 0, wx.TOP, 3)
        simulation_sizer_panel_81.Add(sim_st5, 0, wx.TOP, 8)
        simulation_sizer_panel_81.Add(sim_st6, 0, wx.TOP, 8)

        simulation_sizer_panel_82.Add(t4, 0, wx.TOP, 0)
        simulation_sizer_panel_82.Add(t5, 0, wx.TOP, 0)
        simulation_sizer_panel_82.Add(t6, 0, wx.TOP, 0)

        # CAN ADD MAX 2 MORE ROWS
        simulation_sizer_panel_83.Add(sim_st7, 0, wx.TOP, 3)
        simulation_sizer_panel_84.Add(t7, 0, wx.TOP, 0)

        Sim_Panel1.SetSizer(simulation_sizer1)
        simulation_sizer1.Fit(Sim_Panel1)

        Sim_Panel3.SetSizer(simulation_sizer2)
        simulation_sizer2.Fit(Sim_Panel1)

        Sim_Panel7.SetSizer(simulation_sizer_panel_7)

        Sim_Panel8.SetSizer(simulation_sizer_panel_8)
        # simulation_sizer_panel_8.Fit(Sim_Panel8)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''RESULTS PAGE'''

        Results_Panel1 = RB.RibbonPanel(Results, wx.ID_ANY, "Simulation Choice",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Results_Panel2 = RB.RibbonPanel(Results, wx.ID_ANY, "Tabulated Results",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)

        # CONTROLS
        simulation_results_choices = ["Simulation 1", "Simulation 2", "Simulation 3",
                                      "Simulation 4", "Simulation 5", "Simulation 6"]
        results_cb = wx.ComboBox(Results_Panel1, -1, "Choose Simulation for Result Display", (20, 20),
                          (225, -1), simulation_results_choices, wx.CB_DROPDOWN)

        Results_Bar = RB.RibbonButtonBar(Results_Panel2)

        results_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp5 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        Results_Bar.AddSimpleButton(wx.ID_ANY, "Generate Result Tables", results_bmp1,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Optimization Results", results_bmp2,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Calculations", results_bmp3,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Generate Result Graphs", results_bmp4,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Generate Report", results_bmp5,
                                  "This is a tooltip for adding Nodes")

        simulation_choice_sizer = wx.BoxSizer()
        simulation_choice_sizer.Add(results_cb, 0, wx.TOP|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        Results_Panel1.SetSizer(simulation_choice_sizer)
        simulation_choice_sizer.Fit(Results_Panel1)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''HELP PAGE'''

        Help_Panel = RB.RibbonPanel(Help, wx.ID_ANY, "Help",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)

        Help_Panel_Bar = RB.RibbonButtonBar(Help_Panel)

        help_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        help_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        help_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        help_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        help_bmp5 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Contents", help_bmp1,
                                  "Learn About ASRAD and Pypeline")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "User Manual", help_bmp2,
                                  "Here's our User manual")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Examples", help_bmp3,
                                  "So you don't like to read")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "License Status", help_bmp4,
                                  "")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Licence Add/Remove", help_bmp5,
                                  "This is a tooltip for adding Nodes")

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''REMAINING INIT FOR RIBBON'''

        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self._bitmap_creation_dc.SetFont(label_font)

        # INSTANTIATE RIBBON
        self._ribbon.Realize()

        self.notebook = Notebook(panel)

        # DRAWING FRAMEWORK AND PANEL
        self.graph = PypeGraph.Graph()
        self.drawing_canvas = GDP.GraphDesignPanel(panel, self.graph)

        self.search = TestSearchCtrl(panel)


        # RIBBON SIZERS
        s = wx.BoxSizer(wx.VERTICAL)
        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2a = wx.BoxSizer(wx.VERTICAL)
        s2b = wx.BoxSizer(wx.VERTICAL)

        # We added s2 sizer in s and other sizer in s2
        s.Add(self._ribbon, 0, wx.EXPAND)
        s.Add(s2, 6, wx.EXPAND)
        s2.Add(s2a, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2.Add(s2b, 6, wx.EXPAND)
        # logwindow yerine Demo'dan Toolbar orneginden al
        s2b.Add(self.drawing_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.notebook, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.search, 0, wx.EXPAND | wx.FIXED_MINSIZE)
        self.panel = panel
        panel.SetSizer(s)
        self.SetIcon(images.Mondrian.Icon)
        self.CenterOnScreen()
        self.Maximize()
        self.Show()

        '''BINDING'''
        # self.BindEvents([drawing_tools])
        # NEED TO ADD BUTTON FOR SEPERATE SELECTION OF EDGES VERSUS NODES
        # OR NEED TO COMBINE FUNCTIONALITY

        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddNodesButtonClick, id=ID_NODES)
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onZoomInButtonClick, id=ID_ZOOM_IN )
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onZoomOutButtonClick, id=ID_ZOOM_OUT )
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onPanButtonClick, id=ID_PAN )
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onSelectNodesButtonClick, id=ID_SELECT_NODES)
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onSelectPipesButtonClick, id=ID_SELECT_PIPES)


    # FOR USE WITH FILE MENU

    def OnQuit(self, event):
        self.Close()

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    '''DESIGN PAGE BUTTON BINDING FUNCTIONS'''

    def onAddNodesButtonClick(self, event):
        self.drawing_canvas.SetMode("AddNodes")
        return

    def onZoomInButtonClick(self, event):
        self.drawing_canvas.SetMode("ZoomIn")
        return

    def onZoomOutButtonClick(self, event):
        self.drawing_canvas.SetMode("ZoomOut")
        return

    def onPanButtonClick(self, event):
        self.drawing_canvas.SetMode("Pan")
        return

    def onSelectNodesButtonClick(self, event):
        self.drawing_canvas.SetMode("SelectNodes")
        return
    def onSelectPipesButtonClick(self, event):
        self.drawing_canvas.SetMode("SelectEdges")
        return

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    def OnDrawingPanelClick(self, event):
        pass

    def SetBarStyle(self, agwStyle):

        self._ribbon.Freeze()
        self._ribbon.SetAGWWindowStyleFlag(agwStyle)

        pTopSize = self.panel.GetSizer()
        # pToolbar = wx.FindWindowById(ID_MAIN_TOOLBAR)

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


    def OnNew(self, event):
        pass
        '''USE FOR ADDING NEW PANEL'''


    def OnNewDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "New Document")
        menu.Append(wx.ID_ANY, "New Template")
        menu.Append(wx.ID_ANY, "New Mail")

        event.PopupMenu(menu)

    def OnPrintDropdown(self, event):

        menu = wx.Menu()
        menu.Append(wx.ID_ANY, "Print")
        menu.Append(wx.ID_ANY, "Preview")
        menu.Append(wx.ID_ANY, "Options")

        event.PopupMenu(menu)

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

if __name__ == '__main__':
    app = wx.App()
    frame = RibbonFrame(None, -1, "PypeSim @ASRAD",size=(900, 700))
    frame.Show(True)
    frame.Centre()
    app.MainLoop()
