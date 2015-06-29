from __future__ import division
import wx
import time
import os
import sys
import images
import wx.aui
import wx.lib.agw.ribbon as RB
import ListCtrl
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources, GUIMode
import GraphDesignPanel as  GDP
import PypeGraph as PypeGraph
from TabPanels import NodeTabPanel, PipeTabPanel, ValveTabPanel, CompressorTabPanel, RegulatorTabPanel, LossElementTabPanel


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

def ScaleBitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result
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

'''SEARCH BAR SECTION'''
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


'''LEFT HAND SIDE PANEL NOTEBOOK'''

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
        self.AddPage(NodeTabPanel(self), "ND")
        self.AddPage(PipeTabPanel(self), "PP")
        self.AddPage(ValveTabPanel(self), "VV")
        self.AddPage(CompressorTabPanel(self), "CP")
        self.AddPage(RegulatorTabPanel(self), "RG")
        self.AddPage(LossElementTabPanel(self), "LE")

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
        options_bmp1 = wx.Image("../icons/GeneralSettings.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp2 = wx.Image("../icons/DisplaySettings.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp3 = wx.Image("../icons/UnitSettings.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp4 = wx.Image("../icons/ShortcutSettings.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp5 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp6 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp7 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp8 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp9 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp10 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp11 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp12 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        options_bmp13 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

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
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Mapping On/Off", options_bmp5,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Labels On/Off", options_bmp6,
                                  "This is a tooltip for adding Nodes")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Grid On/Off", options_bmp7,
                                  "This is a tooltip for adding Valves")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Scale On/Off", options_bmp8,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Element Screen On/Off ", options_bmp9,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Outline Screen  On/Off", options_bmp10,
                                  "This is a tooltip for adding Loss Elements")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Calculator On/Off", options_bmp11,
                                  "This is a tooltip for adding Compressors")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "Change to Isometric View On/Off", options_bmp12,
                                  "This is a tooltip for adding Regulators")
        Windows_options_Group.AddToggleButton(wx.ID_ANY, "3D Screen On/Off", options_bmp13,
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
        img_bmp_general_settings = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        img_bmp_display_settings = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        img_bmp_unit_settings = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        img_bmp_short_cut_settings = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()


        # BUTTONS
        # Testen Sie the toggle :)
        # AddToggleButton(self, button_id, label, bitmap, help_string="")

        Images_Group.AddSimpleButton(wx.ID_ANY, "General Settings", img_bmp_general_settings,
                                  "This is a tooltip for adding Nodes")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Display / Labeling Settings", img_bmp_display_settings,
                                  "This is a tooltip for adding Valves")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Unit Settings", img_bmp_unit_settings,
                                  "This is a tooltip for adding Compressors")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Short-Cut Settings", img_bmp_short_cut_settings,
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
        bmp_nodes= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_pipes = wx.Image("../icons/design.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_valves= wx.Image("../icons/Valve.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_compressors= wx.Image("../icons/Compressor.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_regulators= wx.Image("../icons/Regulator.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_loss_ele= wx.Image("../icons/LossElement.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # ICONS for viewing_tools
        bmp6= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp7= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # ICONS for general tools
        bmp_select= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_move= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_delete= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_undo= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp_redo= wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # PANELS IN DESIGN RIBBON PAGE
        _Element_Add = RB.RibbonPanel(Design, wx.ID_ANY, "Add Element", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_General = RB.RibbonPanel(Design, wx.ID_ANY, "Design General", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_View = RB.RibbonPanel(Design, wx.ID_ANY, "Design View", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN DESIGN PAGE
        drawing_tools = RB.RibbonButtonBar(_Element_Add)
        viewing_tools = RB.RibbonButtonBar(_Design_View)
        general_tools = RB.RibbonButtonBar(_Design_General)
        # drawing_tools = RB.RibbonButtonBar(_Element_Add)
        # drawing_tools = RB.RibbonButtonBar(_Element_Add)

        ##MAKE THE BUTTONS
        drawing_tools.AddSimpleButton(ID_NODES, "Nodes", bmp_nodes,
                                  "This is a tooltip for adding Nodes")
        drawing_tools.AddSimpleButton(ID_PIPES, "Pipes", bmp_nodes,
                                  "This is a tooltip for adding Pipes")
        drawing_tools.AddSimpleButton(ID_VALVES, "Valves", bmp_valves,
                                  "This is a tooltip for adding Valves")
        drawing_tools.AddSimpleButton(ID_COMPRESSORS, "Compressors", bmp_compressors,
                                  "This is a tooltip for adding Compressors")
        drawing_tools.AddSimpleButton(ID_REGULATORS, "Regulators", bmp_regulators,
                                  "This is a tooltip for adding Regulators")
        drawing_tools.AddSimpleButton(ID_LOSS_ELEMENTS, "Loss Elements", bmp_loss_ele,
                                  "This is a tooltip for adding Loss Elements")


        viewing_tools.AddSimpleButton(ID_ZOOM_IN, "Zoom In", Resources.getMagPlusBitmap(),
                                  "This is a tooltip for zooming")
        viewing_tools.AddSimpleButton(ID_ZOOM_OUT, "Zoom Out", Resources.getMagMinusBitmap(),
                                  "This is a tooltip for zooming out")
        viewing_tools.AddSimpleButton(ID_PAN, "Panning", Resources.getHandBitmap(),
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

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################

        '''SIMULATION SETTINGS PAGE'''

        # PANELS
        Simulation_General = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "General", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Simulation_Method = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Method", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Default_Values = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Default Values", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Simulation_Control = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Control & Run", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        Simulation_Success = RB.RibbonPanel(Simulation_Settings, wx.ID_ANY, "Simulation Success", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN OPTIONS PAGE
        # SIM METHOD, VALUES AND SUCCESS INCLUDE NON GENERIC WIDGETS, THUS THEY NEED THEIR OWN SIZERS
        Sim_Gen_Group = RB.RibbonButtonBar(Simulation_General)
        Sim_Control_Group = RB.RibbonButtonBar(Simulation_Control)


        # BUTTON ICONS
        # CHANGE CHANGE CHANGE
        sim_bmp1 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp2 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp3 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp4 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp5 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp6 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp7 = wx.Image("../icons/design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        ########################################################################
        # GENERAL PANEL
        ########################################################################
        Sim_Gen_Group.AddSimpleButton(wx.ID_ANY, "General Settings", sim_bmp1,
                                  "This is a tooltip for adding Nodes")
        Sim_Gen_Group.AddSimpleButton(wx.ID_ANY, "Display / Labeling Settings", sim_bmp2,
                                  "This is a tooltip for adding Valves")
        Sim_Gen_Group.AddSimpleButton(wx.ID_ANY, "Unit Settings", sim_bmp3,
                                  "This is a tooltip for adding Compressors")
        Sim_Gen_Group.AddSimpleButton(wx.ID_ANY, "Short-Cut Settings", sim_bmp4,
                                  "This is a tooltip for adding Regulators")

        ########################################################################
        # METHOD PANEL
        ########################################################################

        # ADD CONTROLS
        sim_Text1 = wx.StaticText(Simulation_Method, -1, "Maximum Iteration", (20, 120))
        sim_Text1.SetBackgroundColour(wx.Colour(255, 251, 204))
        sim_Text2 = wx.StaticText(Simulation_Method, -1, "Convergence", (20, 120))
        sim_Text2.SetBackgroundColour(wx.Colour(255, 251, 204))
        sim_Text3 = wx.StaticText(Simulation_Method, -1, "Tolerance", (20, 120))
        sim_Text3.SetBackgroundColour(wx.Colour(255, 251, 204))

        sim_text_control1 = wx.TextCtrl(Simulation_Method, -1, "2300", size=(125, -1))
        sim_text_control2 = wx.TextCtrl(Simulation_Method, -1, "2300", size=(125, -1))
        sim_text_control3 = wx.TextCtrl(Simulation_Method, -1, "2300", size=(125, -1))

        sim_method_button1 = wx.Button(Simulation_Method, -1, "Choose Simulation Method")
        # sim_method_button1.SetBackgroundColour("#c0d890")
        sim_method_button2 = wx.Button(Simulation_Method, -1, "Optimization Options")
        # sim_method_button2.SetBackgroundColour("#c0d890")


        # SIZERS FOR SIM METHOD PANEL TO INCLUDE TEXT CONTROLS AND STATIC TEXT
        # ADD SIZERS APPROPRIATELY
        sim_method_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sim_method_sizer2 = wx.BoxSizer(wx.VERTICAL)
        sim_method_sizer3 = wx.BoxSizer(wx.VERTICAL)

        # Stretch Sizer seems ribbon specific
        sim_method_sizer1.AddStretchSpacer(1)

        sim_method_sizer1.Add(sim_method_sizer2, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer1.Add(sim_method_sizer3, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)

        sim_method_sizer2.Add(sim_method_button1, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer2.Add(sim_method_button2, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)

        sim_method_sizer3.Add(sim_Text1, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer3.Add(sim_text_control1, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer3.Add(sim_Text2, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer3.Add(sim_text_control2, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer3.Add(sim_Text3, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)
        sim_method_sizer3.Add(sim_text_control3, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 2)

        Simulation_Method.SetSizer(sim_method_sizer1)

        ########################################################################
        # DEFAULT VALUES PANEL
        ########################################################################

        # SIZERS FOR DEFAULT VALUES PANEL
        Defualt_topsizer = wx.BoxSizer(wx.VERTICAL)
        Defualt_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        Defualt_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        Defualt_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        Defualt_sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        Defualt_sizer5 = wx.BoxSizer(wx.HORIZONTAL)

        # CONTROLS
        def_Text1 = wx.StaticText(Default_Values, -1, "Altitude On / Off Switch", (20, 120))
        def_Text1.SetBackgroundColour((202,223,244))
        def_Text2 = wx.StaticText(Default_Values, -1, "Default Node Temperature", (20, 120))
        def_Text2.SetBackgroundColour((202,223,244))
        def_Text3 = wx.StaticText(Default_Values, -1, "Default Pipe Equation", (20, 120))
        def_Text3.SetBackgroundColour((202,223,244))
        def_Text4 = wx.StaticText(Default_Values, -1, "Default Ambient Pressure", (20, 120))
        def_Text4.SetBackgroundColour((202,223,244))
        def_Text5 = wx.StaticText(Default_Values, -1, "Default Ambient Temperature", (20, 120))
        def_Text5.SetBackgroundColour((202,223,244))

        Default_panel_button = wx.ToggleButton(Default_Values, -1, "On/Off")

        def_text_control1 = wx.TextCtrl(Default_Values, -1, "2300", size=(125, -1))
        def_text_control2 = wx.TextCtrl(Default_Values, -1, "2300", size=(125, -1))
        def_text_control3 = wx.TextCtrl(Default_Values, -1, "2300", size=(125, -1))

        default_list1 = ['Kelvin', 'Celcius', 'Rankine']
        default_list2 = ['Panhandle A', 'Weymouth', 'Osiadacz is true MotherF#@CKING gangster']
        default_list3 = ['KPa', 'PSI']

        def_choice1 = wx.Choice(Default_Values, -1, (100, 50), choices = default_list1)
        def_choice2 = wx.Choice(Default_Values, -1, (100, 50), choices = default_list2)
        def_choice3 = wx.Choice(Default_Values, -1, (100, 50), choices = default_list3)
        def_choice4 = wx.Choice(Default_Values, -1, (100, 50), choices = default_list1)

        Defualt_topsizer.Add(Defualt_sizer1, 0, wx.ALL|wx.EXPAND, 2)
        Defualt_topsizer.Add(Defualt_sizer2, 0, wx.ALL|wx.EXPAND, 2)
        Defualt_topsizer.Add(Defualt_sizer3, 0, wx.ALL|wx.EXPAND, 2)
        Defualt_topsizer.Add(Defualt_sizer4, 0, wx.ALL|wx.EXPAND, 2)
        Defualt_topsizer.Add(Defualt_sizer5, 0, wx.ALL|wx.EXPAND, 2)

        Defualt_sizer1.Add(def_Text1, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 2)
        Defualt_sizer1.Add(Default_panel_button, 0, wx.ALL|wx.EXPAND | wx.ALIGN_RIGHT, 2)

        Defualt_sizer2.Add(def_Text2, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 2)
        Defualt_sizer2.Add(def_text_control1, 0, wx.ALL|wx.EXPAND | wx.ALIGN_CENTRE, 2)
        Defualt_sizer2.Add(def_choice1, 0, wx.ALL|wx.EXPAND | wx.ALIGN_RIGHT, 2)

        Defualt_sizer3.Add(def_Text3, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 2)
        Defualt_sizer3.Add(def_choice2, 0, wx.ALL|wx.EXPAND | wx.ALIGN_RIGHT, 2)

        Defualt_sizer4.Add(def_Text4, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 2)
        Defualt_sizer4.Add(def_text_control2, 0, wx.ALL|wx.EXPAND | wx.ALIGN_CENTRE, 2)
        Defualt_sizer4.Add(def_choice3, 0, wx.ALL|wx.EXPAND | wx.ALIGN_RIGHT, 2)

        Defualt_sizer5.Add(def_Text5, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 2)
        Defualt_sizer5.Add(def_text_control3, 0, wx.ALL|wx.EXPAND | wx.ALIGN_CENTRE, 2)
        Defualt_sizer5.Add(def_choice4, 0, wx.ALL|wx.EXPAND | wx.ALIGN_RIGHT, 2)

        Default_Values.SetSizer(Defualt_topsizer)

        ########################################################################
        # CONTROL AND RUN PANEL
        ########################################################################

        Sim_Control_Group.AddSimpleButton(wx.ID_ANY, "Check Design Connections", sim_bmp5,
                                  "")
        Sim_Control_Group.AddSimpleButton(wx.ID_ANY, "Initialize and Error Control", sim_bmp6,
                                  "")
        Sim_Control_Group.AddSimpleButton(wx.ID_ANY, "Run Simulation", sim_bmp7,
                                  "")

        ########################################################################
        # SUCCESS PANEL
        ########################################################################

        # SUCCESS SIZERS

        success_topsizer = wx.BoxSizer(wx.VERTICAL)
        success_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        success_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        success_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        success_sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        # SUCCESS CONTROLS
        suc_Text1 = wx.StaticText(Simulation_Success, -1, "Simulation Status", (20, 120))
        suc_Text1.SetBackgroundColour((202,223,244))
        suc_Text2 = wx.StaticText(Simulation_Success, -1, "Simulaion Errors", (20, 120))
        suc_Text2.SetBackgroundColour((202,223,244))
        suc_Text3 = wx.StaticText(Simulation_Success, -1, "Convergence Time", (20, 120))
        suc_Text3.SetBackgroundColour((202,223,244))
        suc_Text4 = wx.StaticText(Simulation_Success, -1, "Total Iteration number", (20, 120))
        suc_Text4.SetBackgroundColour((202,223,244))

        suc_text_control1 = wx.TextCtrl(Simulation_Success, -1, "2300", size=(125, -1))
        suc_text_control2 = wx.TextCtrl(Simulation_Success, -1, "2300", size=(125, -1))
        suc_text_control3 = wx.TextCtrl(Simulation_Success, -1, "2300", size=(125, -1))
        suc_text_control4 = wx.TextCtrl(Simulation_Success, -1, "2300", size=(125, -1))

        success_topsizer.Add(success_sizer1, 0, wx.ALL|wx.EXPAND, 2)
        success_topsizer.Add(success_sizer2, 0, wx.ALL|wx.EXPAND, 2)
        success_topsizer.Add(success_sizer3, 0, wx.ALL|wx.EXPAND, 2)
        success_topsizer.Add(success_sizer4, 0, wx.ALL|wx.EXPAND, 2)

        success_sizer1.Add(suc_Text1, 0, wx.ALL|wx.EXPAND, 2)
        success_sizer1.Add(suc_text_control1, 0, wx.ALL|wx.EXPAND, 2)

        success_sizer2.Add(suc_Text2, 0, wx.ALL|wx.EXPAND, 2)
        success_sizer2.Add(suc_text_control2, 0, wx.ALL|wx.EXPAND, 2)

        success_sizer3.Add(suc_Text3, 0, wx.ALL|wx.EXPAND, 2)
        success_sizer3.Add(suc_text_control3, 0, wx.ALL|wx.EXPAND, 2)

        success_sizer3.Add(suc_Text4, 0, wx.ALL|wx.EXPAND, 2)
        success_sizer3.Add(suc_text_control4, 0, wx.ALL|wx.EXPAND, 2)

        Simulation_Success.SetSizer(success_topsizer)

        ################################################################################################################################################
        ################################################################################################################################################
        ################################################################################################################################################


        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self._bitmap_creation_dc.SetFont(label_font)

        # INSTANTIATE RIBBON
        self._ribbon.Realize()

        self.notebook = Notebook(panel)

        # DRAWING FRAMEWORK AND PANEL
        self.graph = PypeGraph.Graph()
        self.drawing_canvas = GDP.GraphDesignPanel(panel, self.graph)

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
        s.Add(self._ribbon, 0, wx.EXPAND)
        s.Add(s2, 6, wx.EXPAND)
        s2.Add(s2a, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2.Add(s2b, 6, wx.EXPAND)

        # logwindow yerine Demo'dan Toolbar orneginden al
        s2b.Add(self.drawing_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.notebook, 1, wx.EXPAND | wx.FIXED_MINSIZE)
        s2a.Add(self.search, 0, wx.EXPAND | wx.FIXED_MINSIZE)

        panel.SetSizer(s)
        self.panel = panel

        self.SetIcon(images.Mondrian.Icon)
        self.CenterOnScreen()
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
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)


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
    def onSelectPipesButtonClick(self, event):
        self.drawing_canvas.SetMode("SelectEdges")
        return

    def OnDrawingPanelClick(self, event):
        pass

    def onMoveButtonClick(self, event):
        self.drawing_canvas.SetMode("Move")
        return

    def onDeleteButtonClick(self, event):
        if self.graph.focus_node:
            self.graph.deleteNode(self.graph.focus_node.label)
        self.graph.draw(self.drawing_canvas.Canvas)
        self.drawing_canvas.Canvas.Draw()
        self.drawing_canvas.Canvas.ClearAll(ResetBB=False)


    def onUndoButtonClick(self, event):
        self.graph.undo()
        self.graph.draw(self.drawing_canvas.Canvas)
        self.drawing_canvas.Canvas.Draw()
        self.drawing_canvas.Canvas.ClearAll(ResetBB=False)

    def onRedoButtonClick(self, event):
        self.graph.redo()
        self.graph.draw(self.drawing_canvas.Canvas)
        self.drawing_canvas.Canvas.Draw()
        self.drawing_canvas.Canvas.ClearAll(ResetBB=False)

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
