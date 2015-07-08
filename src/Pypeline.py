from __future__ import division
import wx
import time
import os
import sys
import images
import wx.aui
import wx.lib.agw.ribbon as RB
from floatcanvas import Resources
import GraphDesignPanel as  GDP
import PypeGraph as PypeGraph
import TabPanels.NodeTabPanel as NodeTabPanel
import TabPanels.PipeTabPanel as PipeTabPanel
import TabPanels.ValveTabPanel as ValveTabPanel
import TabPanels.CompressorTabPanel as CompressorTabPanel
import TabPanels.RegulatorTabPanel as RegulatorTabPanel
import TabPanels.LossElementTabPanel as LossElementTabPanel
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

## scales a bitmap to the given dimensions
def ScaleBitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result

## creates and returns a scaled bitmap from the image at path
def GetBitmap(path, width=32, height=32):
    bmp = wx.Image(path,wx.BITMAP_TYPE_PNG).ConvertToBitmap()
    return ScaleBitmap(bmp, width, height)

##SOME ID CONSTANTS FOR DESIGN BUTTONS
ID_NODES = wx.ID_HIGHEST + 1
ID_PIPES = ID_NODES + 1
ID_VALVES = ID_NODES + 2
ID_COMPRESSORS = ID_NODES + 3
ID_REGULATORS = ID_NODES + 4
ID_LOSS_ELEMENTS = ID_NODES + 5
ID_ZOOM_IN = ID_NODES + 6
ID_ZOOM_OUT = ID_NODES + 7
ID_PAN = ID_NODES + 8
ID_TOGGLE_MAP = ID_NODES + 9
ID_SELECT = ID_NODES + 10
ID_MOVE = ID_NODES + 11
ID_DELETE = ID_NODES + 12
ID_UNDO = ID_NODES + 13
ID_REDO = ID_NODES + 14
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
                             )
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
        #
        # button_1 = GB.GradientButton(self, -1, None, "File", pos=(0, 0), size=(25, 15))
        # button_1.SetTopEndColour(wx.Colour(135, 206, 250))
        # button_1.SetTopStartColour(wx.Colour(135, 206, 250))
        # button_1.SetBottomEndColour(wx.Colour(30, 144, 255))
        # button_1.SetBottomStartColour(wx.Colour(30, 144, 255))

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

        # COLOR SELECTION
        # RGB VALUE FOR MATTE GREY
        # 204, 204, 204
        primary = wx.Colour(200, 200, 200)
        secondary = wx.Colour(135, 206, 250)
        tertiary = wx.Colour(102, 102, 102)
        self._ribbon.GetArtProvider().SetColourScheme(primary, secondary, tertiary)


        self._bitmap_creation_dc = wx.MemoryDC()
        self._colour_data = wx.ColourData()

        ################################################################################################################################################
        ################################################################################################################################################

        '''RIBBON PAGES'''
        Options = RB.RibbonPage(self._ribbon, wx.ID_ANY, "OPTIONS")
        Mapping = RB.RibbonPage(self._ribbon, wx.ID_ANY, "MAPPING")
        Design = RB.RibbonPage(self._ribbon, wx.ID_ANY, "DESIGN")
        Simulation_Settings = RB.RibbonPage(self._ribbon, wx.ID_ANY, "SIMULATION SETTINGS")
        Results = RB.RibbonPage(self._ribbon, wx.ID_ANY, "RESULTS")
        Help = RB.RibbonPage(self._ribbon, wx.ID_ANY, "HELP")

        ################################################################################################################################################
        ################################################################################################################################################

        '''OPTIONS PAGE'''

        # OPTIONS PAGE'S PANELS
        Options_Settings = RB.RibbonPanel(Options, wx.ID_ANY, "Settings", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Options_Window_Options = RB.RibbonPanel(Options, wx.ID_ANY, "Toggle Design View Options", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN OPTIONS PAGE
        Settings_Group = RB.RibbonButtonBar(Options_Settings)
        Windows_options_Group = RB.RibbonButtonBar(Options_Window_Options)

        # BUTTON ICONS
        # CHANGE CHANGE CHANGE
        options_bmp1 = GetBitmap("../icons/Options/Options_01_General_Settings.png")
        options_bmp2 = GetBitmap("../icons/Options/Options_02_Display_Settings.png")
        options_bmp3 = GetBitmap("../icons/Options/Options_03_Unit_Settings.png")
        options_bmp4 = GetBitmap("../icons/Options/Options_04_ShortCut_Settings.png")
        options_bmp5 = GetBitmap("../icons/Options/Options_05_Mapping.png")
        options_bmp6 = GetBitmap("../icons/Options/Options_06_Labels.png")
        options_bmp7 = GetBitmap("../icons/Options/Options_07_Grid.png")
        options_bmp8 = GetBitmap("../icons/Options/Options_08_Scale.png")
        options_bmp9 = GetBitmap("../icons/Options/Options_09_Element_Screen.png")
        options_bmp10 = GetBitmap("../icons/Options/Options_10_Outline_Screen.png")
        options_bmp11 = GetBitmap("../icons/Options/Options_11_Calculator.png")
        options_bmp12 = GetBitmap("../icons/Options/Options_12_Isometric_View.png")
        options_bmp13 = GetBitmap("../icons/Options/Options_13_3D_Screen.png")


        # BUTTONS
        # Testen Sie the toggle :)
        # AddToggleButton(self, button_id, label, bitmap, help_string="")

        Settings_Group.AddSimpleButton(wx.ID_ANY, "General", options_bmp1,
                                  "This is a tooltip for adding Nodes")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Display", options_bmp2,
                                  "This is a tooltip for adding Valves")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Units", options_bmp3,
                                  "This is a tooltip for adding Compressors")
        Settings_Group.AddSimpleButton(wx.ID_ANY, "Short-Cuts", options_bmp4,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Map View", options_bmp5,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Element Labels", options_bmp6,
                                  "This is a tooltip for adding Nodes")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Grid", options_bmp7,
                                  "This is a tooltip for adding Valves")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Scale Bar", options_bmp8,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Element Editor", options_bmp9,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Mini-Map", options_bmp10,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Calculator", options_bmp11,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Isometric View", options_bmp12,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "3D View", options_bmp13,
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
        options_bmp1 = GetBitmap("../icons/Mapping/Mapping_01_BG_Color.png")
        options_bmp2 = GetBitmap("../icons/Mapping/Mapping_02_Import_Image.png")
        options_bmp3 = GetBitmap("../icons/Mapping/Mapping_03_Delete_Image.png")
        options_bmp4 = GetBitmap("../icons/Mapping/Mapping_04_Image_Settings.png")


        # BUTTONS
        # Testen Sie the toggle :)
        # AddToggleButton(self, button_id, label, bitmap, help_string="")

        Images_Group.AddSimpleButton(wx.ID_ANY, "Background Color", options_bmp1,
                                  "This is a tooltip for adding Nodes")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Import Image", options_bmp2,
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

        # ICONS FOR DESIGN PAGE (MOVE TO GENERAL ICON SECTION LATER)
        # ICONS FOR FIRST PANEL IN DESIGN PAGE
        # VIEWING ICONS ARE TAKEN FROM FLOATCANVAS RESOURCES TO BE REPLACED BY OTHER ICONS LATER

        # ICONS for drawing_tools
        # PLEASE CHANGE ALL BMP ICON NAMES TO REFLECT RELATIVE PANEL
        bmp_nodes= GetBitmap("../icons/Design/Design_01_Node.png")
        bmp_pipes = GetBitmap("../icons/Design/Design_02_Pipe.png")
        bmp_valves= GetBitmap("../icons/Design/Design_03_Valve.png")
        bmp_compressors= GetBitmap("../icons/Design/Design_04_Compressor.png")
        bmp_regulators= GetBitmap("../icons/Design/Design_05_Regulator.png")
        bmp_loss_ele= GetBitmap("../icons/Design/Design_06_Loss_Element.png")



        # ICONS for general tools
        bmp_select= GetBitmap("../icons/Design/Design_07_Selection.png")
        bmp_move = GetBitmap("../icons/Design/Design_08_Drag.png")
        bmp_delete = GetBitmap("../icons/Design/Design_09_Delete.png")
        bmp_undo = GetBitmap("../icons/Design/Design_10_Undo.png")
        bmp_redo = GetBitmap("../icons/Design/Design_11_Redo.png")

        # ICONS for viewing_tools
        bmp_ZoomIn = GetBitmap("../icons/Design/Design_12_Zoom_In.png")
        bmp_ZoomOut = GetBitmap("../icons/Design/Design_12_Zoom_Out.png")
        bmp_Pan = GetBitmap("../icons/Design/Design_14_Panning.png")

        bmp_element_list = GetBitmap("../icons/Design/Design_15_Element_List.png")
        bmp_element_display = GetBitmap("../icons/Design/Design_16_Element_Display.png")
        bmp_Ok_for_Coord = GetBitmap("../icons/Design/Design_17_OK_For_Coord.png")



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
        drawing_tools.AddSimpleButton(ID_NODES, "Nodes", bmp_nodes,
                                  "This is a tooltip for adding Nodes")
        drawing_tools.AddSimpleButton(ID_PIPES, "Pipes", bmp_pipes,
                                  "This is a tooltip for adding Pipes")
        drawing_tools.AddSimpleButton(ID_VALVES, "Valves", bmp_valves,
                                  "This is a tooltip for adding Valves")
        drawing_tools.AddSimpleButton(ID_COMPRESSORS, "Compressors", bmp_compressors,
                                  "This is a tooltip for adding Compressors")
        drawing_tools.AddSimpleButton(ID_REGULATORS, "Regulators", bmp_regulators,
                                  "This is a tooltip for adding Regulators")
        drawing_tools.AddSimpleButton(ID_LOSS_ELEMENTS, "Loss Elements", bmp_loss_ele,
                                  "This is a tooltip for adding Loss Elements")


        viewing_tools.AddSimpleButton(ID_ZOOM_IN, "Zoom In", bmp_ZoomIn,
                                  "This is a tooltip for zooming")
        viewing_tools.AddSimpleButton(ID_ZOOM_OUT, "Zoom Out", bmp_ZoomOut,
                                  "This is a tooltip for zooming out")
        viewing_tools.AddSimpleButton(ID_PAN, "Panning", bmp_Pan,
                                  "This is a tooltip for panning")

        general_tools.AddSimpleButton(ID_SELECT, "Select", bmp_select,
                                  "This is a tooltip for selecting")
        general_tools.AddSimpleButton(ID_MOVE, "Move", bmp_move,
                                  "This is a tooltip for selecting")
        general_tools.AddSimpleButton(ID_DELETE, "Delete", bmp_delete,
                                  "This is a tooltip for deleting elements")
        general_tools.AddSimpleButton(ID_UNDO, "Undo", bmp_undo,
                                  "This is a tooltip to Undo")
        general_tools.AddSimpleButton(ID_REDO, "Redo", bmp_redo,
                                  "This is a tooltip to Redo")

        element_tools.AddSimpleButton(wx.ID_ANY, "Element List", bmp_element_list,
                                   "Tool tip")
        element_tools.AddSimpleButton(wx.ID_ANY, "Element Display", bmp_element_display,
                                  "This is a tooltip to change element properties")

        # SIZER FOR COORDINATES PANEL
        coord_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ## sizer for inside coord_sizer
        xy_sizer = wx.BoxSizer(wx.VERTICAL)

        # CONTROLS FOR COORDINATES PANEL
        coord_x = wx.TextCtrl(_Coordinate_Control, -1, "", size=(80, -1))
        coord_y = wx.TextCtrl(_Coordinate_Control, -1, "", size=(80, -1))

        coord_button_1 = GB.GradientButton(_Coordinate_Control, -1, None, "OK", (100, 50), size=(30,30))
        coord_button_1.SetTopStartColour(wx.Colour(0,77,243,255))
        coord_button_1.SetTopEndColour(wx.Colour(0,77,253,255))
        coord_button_1.SetBottomStartColour(wx.Colour(0,77,233,255))
        coord_button_1.SetBottomEndColour(wx.Colour(0,77,243,255))

        # coord_button_1.SetForegroundColour(wx.Colour(0,0,0,255))
        coord_button_1.SetBackgroundColour(wx.Colour(0,77,253,255))
        coord_button_1.SetPressedTopColour(wx.Colour(0,77,253,255))
        coord_button_1.SetPressedBottomColour(wx.Colour(0,77,253,255))

        xy_sizer.Add(coord_x, 0,wx.TOP|wx.RIGHT|wx.LEFT, 5)
        xy_sizer.Add(coord_y, 0,wx.TOP|wx.RIGHT|wx.LEFT, 5)
        coord_sizer.Add(xy_sizer, 1, wx.ALL, 1)
        coord_sizer.Add(coord_button_1, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)

          # SET SIZER FOR _Coordinate_Control
        _Coordinate_Control.SetSizer(coord_sizer)
        coord_sizer.Fit(_Coordinate_Control)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''SIMULATION SETTINGS PAGE'''

        Sim_Panel1 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel2 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Settings",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel3 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Check and Run",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel4 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Details",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)
        Sim_Panel5 = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Success",
                                     wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=RB.RIBBON_PANEL_DEFAULT_STYLE)

        #######################################################################################

        sim_bmp1 = GetBitmap("../icons/Simulation/Simulation_01_Simulation.png")
        sim_bmp2 = GetBitmap("../icons/Simulation/Simulation_02_Simulation_Settings.png")
        sim_bmp3 = GetBitmap("../icons/Simulation/Simulation_03_Fluid_Settings.png")
        sim_bmp4 = GetBitmap("../icons/Simulation/Simulation_04_Display_Settings.png")
        sim_bmp5 = GetBitmap("../icons/Simulation/Simulation_05_Initialize.png")
        sim_bmp6 = GetBitmap("../icons/Simulation/Simulation_06_Run.png")

        Sim_Bar1 = RB.RibbonButtonBar(Sim_Panel2)
        Sim_Bar2 = RB.RibbonButtonBar(Sim_Panel3)

           # CONTROLS FOR PANEL 1
        simulation_choices1 = ["Simulation 1", "Simulation 2", "Simulation 3",
                                      "Simulation 4", "Simulation 5", "Simulation 6"]
        simulation_choices2 = ["Steady State", "Transient", "Steady State with Heat Transfer",]

        sim_cb1 = wx.ComboBox(Sim_Panel1, -1, "Choose Design to Simulate", (20,20),
                          (188, -1), simulation_choices1, wx.CB_DROPDOWN)
        sim_cb2 = wx.ComboBox(Sim_Panel1, -1, "Choose Method for Simulation", (20, 20),
                          (188, -1), simulation_choices2, wx.CB_DROPDOWN)

        # CONTROLS FOR PANEL 2
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Simulation", sim_bmp1,
                                  "Create and Name a new design in the drawing window")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Simulation Settings", sim_bmp2,
                                  "Colour range selection and labels for Design")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Fluid Properties", sim_bmp3,
                                  "Choose and Edit Fluid Properties")
        Sim_Bar1.AddSimpleButton(wx.ID_ANY, "Display Settings", sim_bmp4,
                                  "Colour Range Selection and Labels for Design")

        # CONTROLS FOR PANEL 3
        Sim_Bar2.AddSimpleButton(wx.ID_ANY, "Initialize", sim_bmp5,
                                  "Checks connections and parameters")
        Sim_Bar2.AddSimpleButton(wx.ID_ANY, "Run", sim_bmp6,
                                  "Run selected simulation")

        # CONTROLS FOR PANEL 4
        simulation_trans_text1 = TransparentText(Sim_Panel4, -1, "Maximum Iteration", size=wx.DefaultSize)
        simulation_trans_text2 = TransparentText(Sim_Panel4, -1, "Convergence", size=wx.DefaultSize)
        simulation_trans_text3 = TransparentText(Sim_Panel4, -1, "Tolerance", size=wx.DefaultSize)

        simulation_t1 = wx.TextCtrl(Sim_Panel4, -1, "", size=wx.DefaultSize)
        simulation_t2 = wx.TextCtrl(Sim_Panel4, -1, "", size=wx.DefaultSize)
        simulation_t3 = wx.TextCtrl(Sim_Panel4, -1, "", size=wx.DefaultSize)

        # CONTROLS FOR PANEL 5
        simulation_trans_text4 = TransparentText(Sim_Panel5, -1, "Simulation Status", size=wx.DefaultSize)
        simulation_trans_text5 = TransparentText(Sim_Panel5, -1, "Simulation Errors", size=wx.DefaultSize)
        simulation_trans_text6 = TransparentText(Sim_Panel5, -1, "Convergence Time", size=wx.DefaultSize)
        simulation_trans_text7 = TransparentText(Sim_Panel5, -1, "Total Iteration", size=wx.DefaultSize)

        t4 = wx.TextCtrl(Sim_Panel5, -1, "", size=wx.DefaultSize)
        t5 = wx.TextCtrl(Sim_Panel5, -1, "", size=wx.DefaultSize)
        t6 = wx.TextCtrl(Sim_Panel5, -1, "", size=wx.DefaultSize)
        t7 = wx.TextCtrl(Sim_Panel5, -1, "", size=wx.DefaultSize)

        # SIZERS FOR PANEL 1
        simulation_sizer1 = wx.BoxSizer(wx.VERTICAL)

        simulation_sizer1.Add(sim_cb1, 0, wx.TOP, 15)
        simulation_sizer1.Add(sim_cb2, 0, wx.BOTTOM, 5)

        Sim_Panel1.SetSizer(simulation_sizer1)
        simulation_sizer1.Fit(Sim_Panel1)

         # SIZERS FOR PANEL 4
        simulation_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer3 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer4 = wx.BoxSizer(wx.VERTICAL)

        simulation_sizer2.Add(simulation_sizer3, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer2.Add(simulation_sizer4, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)

        simulation_sizer3.Add(simulation_trans_text1, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 3)
        simulation_sizer3.Add(simulation_trans_text2, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 8)
        simulation_sizer3.Add(simulation_trans_text3, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 8)

        simulation_sizer4.Add(simulation_t1, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer4.Add(simulation_t2, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer4.Add(simulation_t3, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)

        Sim_Panel4.SetSizer(simulation_sizer2)
        simulation_sizer2.Fit(Sim_Panel4)

        # SIZERS FOR PANEL 5
        simulation_sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer6 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer7 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer8 = wx.BoxSizer(wx.VERTICAL)
        simulation_sizer9 = wx.BoxSizer(wx.VERTICAL)

        simulation_sizer5.Add(simulation_sizer6, 1, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer5.Add(simulation_sizer7, 1, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer5.Add(simulation_sizer8, 1, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer5.Add(simulation_sizer9, 1, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)

        simulation_sizer6.Add(simulation_trans_text4, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 3)
        simulation_sizer6.Add(simulation_trans_text5, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 8)
        simulation_sizer6.Add(simulation_trans_text6, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 8)

        simulation_sizer7.Add(t4, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer7.Add(t5, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        simulation_sizer7.Add(t6, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)

        simulation_sizer8.Add(simulation_trans_text7, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 3)

        simulation_sizer9.Add(t7, 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL, 0)

        Sim_Panel5.SetSizer(simulation_sizer5)
        simulation_sizer5.Fit(Sim_Panel5)

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

        results_bmp1 = wx.Image("../icons/Results/Results_01_Result_Tables.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp2 = wx.Image("../icons/Results/Results_02_Optimization.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp3 = wx.Image("../icons/Results/Results_03_Calculations.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp4 = wx.Image("../icons/Results/Results_04_Result_Graphs.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        results_bmp5 = wx.Image("../icons/Results/Results_05_Generate_Report.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        Results_Bar.AddSimpleButton(wx.ID_ANY, "Result Tables", results_bmp1,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Optimization Results", results_bmp2,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Calculations", results_bmp3,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Result Graphs", results_bmp4,
                                  "This is a tooltip for adding Nodes")
        Results_Bar.AddSimpleButton(wx.ID_ANY, "Report", results_bmp5,
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

        help_bmp1 = GetBitmap("../icons/Help/Help_01_Contents.png")
        help_bmp2 = GetBitmap("../icons/Help/Help_02_User_Manuel.png")
        help_bmp3 = GetBitmap("../icons/Help/Help_03_Examples.png")
        help_bmp4 = GetBitmap("../icons/Help/Help_04_Licence.png")
        help_bmp5 = GetBitmap("../icons/Help/Help_05_Ask_About.png")
        help_bmp6 = GetBitmap("../icons/Help/Help_06_Web_Page.png")
        help_bmp7 = GetBitmap("../icons/Help/Help_07_About.png")

        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Contents", help_bmp1,
                                  "Learn About ASRAD and Pypeline")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "User Manual", help_bmp2,
                                  "Here's our User manual")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Examples", help_bmp3,
                                  "So you don't like to read")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "License", help_bmp4,
                                  "License")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Ask About", help_bmp5,
                                  "This is a tooltip for adding Nodes")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "Web Page", help_bmp6,
                                  "This is a tooltip for adding Nodes")
        Help_Panel_Bar.AddSimpleButton(wx.ID_ANY, "About", help_bmp7,
                                  "This is a tooltip for adding Nodes")

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''REMAINING INITIALIZATION FOR RIBBON'''

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
        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddPipesButtonClick, id=ID_PIPES)
        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddValvesButtonClick, id=ID_VALVES)
        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddRegulatorsButtonClick, id=ID_REGULATORS)
        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddCompressorsButtonClick, id=ID_COMPRESSORS)
        drawing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onAddLossElementsButtonClick, id=ID_LOSS_ELEMENTS)
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onZoomInButtonClick, id=ID_ZOOM_IN )
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onZoomOutButtonClick, id=ID_ZOOM_OUT )
        viewing_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onPanButtonClick, id=ID_PAN )
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onSelectButtonClick, id=ID_SELECT)
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onMoveButtonClick, id=ID_MOVE)
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onDeleteButtonClick, id=ID_DELETE)
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onUndoButtonClick, id=ID_UNDO)
        general_tools.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onRedoButtonClick, id=ID_REDO)

    # FOR USE WITH FILE MENU

    def OnQuit(self, event):
        self.Close()

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    '''DESIGN PAGE BUTTON BINDING FUNCTIONS'''

    def onKeyDown(self, event):
        print "FUCK"
        keycode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.SetMode("Select")


    def onAddNodesButtonClick(self, event):
        self.drawing_canvas.SetMode("AddNodes")
        return

    def onAddPipesButtonClick(self, event):
        self.drawing_canvas.SetMode("AddPipes")
        return

    def onAddValvesButtonClick(self, event):
        self.drawing_canvas.SetMode("AddValves")
        return

    def onAddRegulatorsButtonClick(self, event):
        self.drawing_canvas.SetMode("AddRegulators")
        return

    def onAddCompressorsButtonClick(self, event):
        self.drawing_canvas.SetMode("AddCompressors")
        return

    def onAddLossElementsButtonClick(self, event):
        self.drawing_canvas.SetMode("AddLossElements")
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

    def onSelectButtonClick(self, event):
        self.drawing_canvas.SetMode("Select")
        return

    def OnDrawingPanelClick(self, event):
        pass

    def onMoveButtonClick(self, event):
        self.drawing_canvas.SetMode("Move")
        return

    def onDeleteButtonClick(self, event):
        if self.graph.focus_node:
            self.graph.deleteNode(self.graph.focus_node)
        elif self.graph.focus_edge:
            self.graph.deleteEdge(self.graph.focus_edge)

        self.drawing_canvas.update()


    def onUndoButtonClick(self, event):
        self.graph.undo()
        self.drawing_canvas.update()

    def onRedoButtonClick(self, event):
        self.graph.redo()
        self.drawing_canvas.update()



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
