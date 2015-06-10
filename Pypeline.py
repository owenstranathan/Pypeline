from __future__ import division
import wx
import time
import os
import sys
import images
import wx.aui
import wx.lib.scrolledpanel as scrolled
import wx.dataview as dv
import wx.lib.mixins.listctrl as listmix
import wx.lib.agw.ribbon as RB
import ListCtrl
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources, GUIMode
import GraphDesignPanel as  GDP
import PypeGraph as PypeGraph

# http://wxpython.org/Phoenix/docs/html/lib.agw.ribbon.buttonbar.RibbonButtonBar.html
########################################################################

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

'''LEFT MENU STARTS FROM HERE (NOTEBOOK)'''

# '''Pipe Flow Equation Choose We Are Not Using Now'''
#
# class SingleChoice(wx.Panel):
#     def __init__(self, parent):
#         wx.Panel.__init__(self, parent, -1)
#
#         sampleList = ['Choose Flow Eq.', 'General Pipe Eq.', 'Weymouth Eq.', 'Aga Eq.', 'Panhandle A Eq.',
#                       'Panhandle B Eq.', 'IGT Eq.', 'Spitzglass (HP) Eq.']
#
#         self.ch = wx.Choice(self, -1, (20, 50), (130, 50),choices = sampleList,style=0)
#         self.ch.SetSelection(0)
#         self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.ch)
#
#
#     def EvtChoice(self, event):
#         self.log.WriteText('EvtChoice: %s\n' % event.GetString())
#         self.ch.Append("A new item")
#
#         if event.GetString() == 'one':
#             self.log.WriteText('Well done!\n')

################################################################################################################################################
'''LIST PANEL SECTION'''

'''FOR USE IN LIST PANEL'''
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
        wx.MessageBox("Do You Want to Delete XXX?", 'Delete Warning!', wx.OK | wx.CANCEL)

        for row in rows:
            # remove it from our data structure
            del self.data[row]
            # notify the view(s) using this model that it has been removed
            self.RowDeleted(row)

        wx.MessageBox('XXX Deleted', 'Delete Information',wx.OK)


    def AddRow(self, value):
        # update data structure
        self.data.append(value)
        # notify views
        self.RowAppended()

'''LIST PANEL MAIN CLASS'''

class ListPanel(wx.Panel):


    def __init__(self, parent, model=None, data=None):
        wx.Panel.__init__(self, parent, -1,size=(60,250))

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

################################################################################################################################################
'''INFO PANEL SECTION'''

'''FOR USE IN INFO PANEL FIRST ROW'''
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(240,50), style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

class DenemeListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        rows = [("NN1", "Kadikoy", "1996")
                ]
        self.list_ctrl = EditableListCtrl(self, style=wx.LC_REPORT)

        self.list_ctrl.InsertColumn(0, "NODE NO", width=65)
        self.list_ctrl.InsertColumn(1, "TITLE", width=110)
        self.list_ctrl.InsertColumn(2, "LABEL", width=60)


        index = 0
        for row in rows:
            self.list_ctrl.InsertStringItem(index, row[0])
            self.list_ctrl.SetStringItem(index, 1, row[1])
            self.list_ctrl.SetStringItem(index, 2, row[2])
            index += 1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.FIXED_MINSIZE|wx.CENTRE|wx.TOP, 0)
        self.SetSizer(sizer)

'''LINKS FOR USE IN INFO PANEL'''

class NodeLinksPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        text1 = wx.StaticText(self, -1, "LINKS :")
        ctrl1 = wx.TextCtrl(self, -1, "PP3 PP232 PP34543")

        sizer.Add(text1, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE,5)
        sizer.Add(ctrl1, 5, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE,5)

        self.SetSizer(sizer)

'''COMMENT LINE FOR USE IN INFO PANEL'''
class NodeCommentPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        text1 = wx.StaticText(self, -1, "COMMENT :")
        ctrl1 = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

        sizer.Add(text1, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE,5)
        sizer.Add(ctrl1, 6, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE,5)

        self.SetSizer(sizer)

'''NODE TYPE CHOOSE FOR USE IN INFO PANEL'''
class NodeSingleChoicePanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        choices = [u"Demand Node",u"Source Node", u"Junction Node", u"Wellhead"]
        self.ch= wx.Choice(self, wx.ID_ANY, choices=choices)
        self.ch.SetSelection(0)

class NodeTypePanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        text1 = wx.StaticText(self, -1, "NODE TYPE :")

        sizer.Add(text1, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE,5)
        sizer.Add(NodeSingleChoicePanel(self),2, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.SetSizer(sizer)

'''INFO PANEL MAIN CLASS'''

class InfoPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,180))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(DenemeListPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(NodeLinksPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(NodeCommentPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(NodeTypePanel(self), 0, wx.ALL|wx.EXPAND, 0)

        self.SetSizer(sizer)
        sizer.Fit(self)

################################################################################################################################################
'''PHYSICAL PANEL SECTION'''

'''ALTITUDE UNITE SELECTION FOR USE IN PHYSICAL PANEL'''
class AltUnitSingleChoice(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        altitudeunitlist = ['Meters', 'Feet']

        self.ch = wx.Choice(self, -1, size=(60, 50),choices = altitudeunitlist)
        self.ch.SetSelection(0)

'''PHYSICAL PANEL MAIN CLASS'''
class PhysicalPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        bmp= wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        button = wx.BitmapButton(self, -1, bmp, (20, 20),
                       (bmp.GetWidth(), bmp.GetHeight()))
        button.SetToolTipString("Coordinate Selection From Map")

        l1 = wx.StaticText(self, -1, "X COORD.")
        t1 = wx.TextCtrl(self, -1, "12346566", size=(80, -1))
        l2 = wx.StaticText(self, -1, "Y COORD.")
        t2 = wx.TextCtrl(self, -1, "12314566", size=(80, -1))
        l3 = wx.StaticText(self, -1, "ALTITUDE")
        t3 = wx.TextCtrl(self, -1, "1200", size=(80, -1))

        sizerphysical = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=1)
        sizerphysical1 = wx.FlexGridSizer(rows=3, cols=2, hgap=15, vgap=1)
        sizerphysical1.SetFlexibleDirection( wx.BOTH )
        sizerphysical1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sizerphysical1.AddMany([ l1, t1,
                        l2, t2,
                        l3, t3])

        sizerphysical2 = wx.BoxSizer(wx.VERTICAL)
        sizerphysical.Add(sizerphysical1, 1, wx.ALL|wx.EXPAND, 0)
        sizerphysical.Add(sizerphysical2, 1, wx.ALL, 0)
        sizerphysical2.Add(button, 1, wx.TOP|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizerphysical2.Add(AltUnitSingleChoice(self), 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)


        sizer.Add(sizerphysical, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        sizerphysical.Fit(self)

################################################################################################################################################
'''PROPERTIES PANEL SECTION'''
'''---------------------------------------'''

''' RADIO METHOD PANEL FOR USE IN PROPERTIES PANEL'''

'''FLOW RATE UNITE SELECTION FOR USE IN RADIO METHOD PANEL'''
class FlowUnitSingleChoice(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        flowunitlist = ['m3/s', 'ft3/s']

        self.ch = wx.Choice(self, -1, size=(60, 50),choices = flowunitlist)
        self.ch.SetSelection(0)

'''PRESSURE UNITE SELECTION FOR USE IN RADIO METHOD PANEL'''
class PresUnitSingleChoice(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        presunitlist = ['KPa', 'Pa', 'atm', 'Psi','bar']

        self.ch = wx.Choice(self, -1, size=(60, 50),choices = presunitlist)
        self.ch.SetSelection(0)

''' RADIO METHOD PANEL '''
class NodeMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # CONTROLS:

        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox( panel, -1, "METHOD SELECTION" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=3 )

        # 1st group of controls:
        self.group1_ctrls = []
        radio1 = wx.RadioButton( panel, -1, "Non", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "Flow" )
        radio3 = wx.RadioButton( panel, -1, "Pressure" )
        text1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )
        text2 = wx.TextCtrl( panel, -1, "",size=(70, -1 ))
        text3 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        unit1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )
        self.group1_ctrls.append((radio1, text1, unit1))
        self.group1_ctrls.append((radio2, text2, FlowUnitSingleChoice(panel)))
        self.group1_ctrls.append((radio3, text3, PresUnitSingleChoice(panel)))

        for radio, text, unit in self.group1_ctrls:
            grid1.Add( radio, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (0,10) )
        self.panel = panel

        # Setup event handling and initial state for controls:
        for radio, text, textxxx in self.group1_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, radio )

    def OnGroup1Select( self, event ):
        radio_selected = event.GetEventObject()

        for radio, text, unit in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
                unit.Enable(True)
            else:
                text.Enable(False)
                unit.Enable(False)

#---------------------------------------#

'''TEMPERATURE UNITE SELECTION FOR USE IN TEMPERATURE RADIO METHOD PANEL'''
class TempUnitSingleChoice(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        tempunitlist = ['Kelvin', 'Celcius']

        self.ch = wx.Choice(self, -1, size=(60, 50),choices = tempunitlist)
        self.ch.SetSelection(0)


''' TEMPERATURE RADIO METHOD PANEL FOR USE IN PROPERTIES PANEL'''

class NodeTempMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # CONTROLS:

        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox( panel, -1, "TEMPERATURE OPTIONS" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=3 )

        # 1st group of controls:
        self.group1_ctrls = []
        radio1 = wx.RadioButton( panel, -1, "Sim. Def.", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "User Def." )
        text1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )
        text2 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        unit1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )

        self.group1_ctrls.append((radio1, text1, unit1))
        self.group1_ctrls.append((radio2, text2, TempUnitSingleChoice(panel)))
        # self.group1_ctrls.append((radio3, text3))

        for radio, text, unit in self.group1_ctrls:
            grid1.Add( radio, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (0,10) )
        self.panel = panel

        # Setup event handling and initial state for controls:
        for radio, text, unit in self.group1_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, radio )

    def OnGroup1Select( self, event ):
        radio_selected = event.GetEventObject()

        for radio, text, unit in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
                unit.Enable(True)
            else:
                text.Enable(False)
                unit.Enable(False)

#---------------------------------------#

'''PRESSURE UNITE SELECTION FOR USE IN WELLHEAD PANEL'''
class PresWellheadUnitSingleChoice(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        presunitlist = ['KPa', 'Pa', 'atm', 'Psi','bar']

        self.ch = wx.Choice(self, -1, size=(60, 50),choices = presunitlist)
        self.ch.SetSelection(0)


''' SPIN PANEL FOR USE IN PROPERTIES PANEL'''

class WellHeadExpSpinPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        spin = wx.SpinCtrlDouble(self, value='0.95', size=(70,-1),style=wx.SP_ARROW_KEYS,
                                 min=0.50, max=0.99, inc=0.01)
        spin.SetDigits(2)


''' WELLHEAD PANEL FOR USE IN PROPERTIES PANEL'''

class WellheadMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # Layout controls on panel:

        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox( panel, -1, "WELLHEAD INPUT" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=3 )

        # 1st group of controls:
        self.group1_ctrls = []
        title1 = wx.StaticText( panel, -1, "Cut-Off Pres.",size=(70, -1 ) )
        title2 = wx.StaticText( panel, -1, "Exponent",size=(70, -1 ) )
        input1 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        unit1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )

        self.group1_ctrls.append((title1, input1, PresWellheadUnitSingleChoice(panel)))
        self.group1_ctrls.append((title2, WellHeadExpSpinPanel(panel), unit1))

        for title, text, unit in self.group1_ctrls:
            grid1.Add( title, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (0,10) )
        self.panel = panel


'''PROPERTIES PANEL MAIN CLASS'''

class NodePropertiesPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,100))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(NodeMethodRadioPanel(self), 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add(NodeTempMethodRadioPanel(self), 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add(WellheadMethodRadioPanel(self), 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)

################################################################################################################################################

'''NODE TAB SECTION'''

class NodeTabPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.SetBackgroundColour((202,223,244))
        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(ListPanel(self, None, data=nodedata), 1, wx.ALL|wx.EXPAND | wx.FIXED_MINSIZE, 3)

        sizer.Add(sizer2, 3, wx.ALL, 5)

        sizer2.Add(InfoPanel(self), 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
        sizer2.Add(PhysicalPanel(self), 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
        sizer2.Add(NodePropertiesPanel(self), 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)

        self.SetSizerAndFit(sizer)
        #sizer1.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()

################################################################################################################################################

class ValveListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        rows = [("NN1", "Kadikoy", "1996")
                ]
        self.list_ctrl = EditableListCtrl(self, style=wx.LC_REPORT)

        self.list_ctrl.InsertColumn(1, "VALVE NO", width=70)
        self.list_ctrl.InsertColumn(1, "TITLE", width=100)
        self.list_ctrl.InsertColumn(1, "LABEL", width=60)


        index = 0
        for row in rows:
            self.list_ctrl.InsertStringItem(index, row[0])
            self.list_ctrl.SetStringItem(index, 1, row[1])
            self.list_ctrl.SetStringItem(index, 2, row[2])
            index += 1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.FIXED_MINSIZE|wx.ALIGN_LEFT|wx.TOP, 0)
        self.SetSizer(sizer)

class ValvePhysicalPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        bmp = wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        button = wx.BitmapButton(self, -1, bmp, (20, 20),
                       (bmp.GetWidth(), bmp.GetHeight()))
        button.SetToolTipString("Coordinate Selection From Map")

        l1 = wx.StaticText(self, -1, "X COORD.")
        t1 = wx.TextCtrl(self, -1, "12346566", size=(80, -1))
        l2 = wx.StaticText(self, -1, "Y COORD.")
        t2 = wx.TextCtrl(self, -1, "12314566", size=(80, -1))
        l3 = wx.StaticText(self, -1, "ALTITUDE")
        t3 = wx.TextCtrl(self, -1, "1200", size=(80, -1))

        l4 = wx.StaticText(self, -1, "SUCTION DISTANCE:")
        t4 = wx.TextCtrl(self, -1, "2300", size=(80, -1))
        Suction_Distance_Choices = ['Km', 'Miles']
        Suction_Distance_Choice = wx.Choice(self, -1, size=(60, 50),choices = Suction_Distance_Choices)
        Suction_Distance_Choice.SetSelection(0)


        sizerphysical = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=1)
        sizerphysical1 = wx.FlexGridSizer(rows=3, cols=2, hgap=15, vgap=1)
        sizerphysical1.SetFlexibleDirection( wx.BOTH )
        sizerphysical1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sizerphysical1.AddMany([ l1, t1,
                        l2, t2,
                        l3, t3])

        sizerphysical2 = wx.BoxSizer(wx.VERTICAL)
        sizerphysical.Add(sizerphysical1, 1, wx.ALL|wx.EXPAND, 0)
        sizerphysical.Add(sizerphysical2, 1, wx.ALL, 0)
        sizerphysical2.Add(button, 1, wx.TOP|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizerphysical2.Add(AltUnitSingleChoice(self), 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        Bottom_Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Bottom_Sizer.Add(l4,0,wx.ALIGN_LEFT, 0)
        Bottom_Sizer.Add(t4,0,wx.ALIGN_LEFT, 0)
        Bottom_Sizer.Add(Suction_Distance_Choice,0,wx.ALIGN_LEFT, 0)

        sizer.Add(sizerphysical, 0, wx.ALL|wx.EXPAND | wx.ALIGN_BOTTOM, 5)
        sizer.Add(Bottom_Sizer, 0, wx.ALL | wx.EXPAND| wx.ALIGN_TOP, 5)


        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        sizerphysical.Fit(self)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, evt):
        if self.GetAutoLayout():
            self.Layout()


class ValveInfoPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,180))

        self.staticText1 = wx.StaticText(self, -1, "CON. PIPE")
        self.staticText2 = wx.StaticText(self, -1, "SUCTION")
        self.staticText3 = wx.StaticText(self, -1, "DISCHARGE")
        self.staticText4 = wx.StaticText(self, -1, "COMMENT")

        self.staticText1ctrl1 = wx.TextCtrl(self, -1, "P123")
        self.staticText3ctrl2 = wx.TextCtrl(self, -1, "N32")
        self.staticText1ctrl3 = wx.TextCtrl(self, -1, "Comment")

        choices = [u"N2", u"Source Node", u"Junction Node", u"Wellhead"]
        self.choice1 = wx.Choice(self, -1, choices=choices)
        self.choice1.SetSelection(0)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        sizer1.Add(ValveListPanel(self), 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer2, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer3, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer4, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(ValvePhysicalPanel(self), 1, wx.ALL|wx.EXPAND, 0)

        sizer2.Add(self.staticText1, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.staticText2, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.staticText3, 1, wx.ALL|wx.EXPAND, 5)

        sizer3.Add(self.staticText1ctrl1, 0, wx.ALL|wx.EXPAND, 5)
        sizer3.Add(self.choice1, 0, wx.ALL|wx.EXPAND, 5)
        sizer3.Add(self.staticText3ctrl2, 0, wx.ALL|wx.EXPAND, 5)

        sizer4.Add(self.staticText4, 0, wx.ALL|wx.EXPAND, 5)
        sizer4.Add(self.staticText1ctrl3, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer1)
        sizer1.Fit(self)
        # self.SetAutoLayout(1)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, evt):
        if self.GetAutoLayout():
            self.Layout()


class ValveMethodPanel( wx.Panel ):
    def __init__( self, parent ):

        wx.Panel.__init__( self, parent, -1 )
        panel = wx.Panel( self, -1 )

        # Layout controls on panel:
        Sizer1 = wx.BoxSizer( wx.VERTICAL )
        box1_title = wx.StaticBox( panel, -1, "METHOD SELECTION" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.FlexGridSizer( cols=2 )
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        # CONTROLS:
        sampleList = ['Choose Valve Type', 'one', 'two', 'three', 'four', 'five',
                      #'this is a long item that needs a scrollbar...',
                      'six', 'seven', 'eight']
        combobox = wx.ComboBox(panel, 500, "Choose Valve Type", (90, 50),
                         (160, -1), sampleList,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )
        TextCtrl1 = wx.TextCtrl(self, -1, "Status")
        self.group1_ctrls = []

        radio1 = wx.RadioButton( panel, -1, "", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "" )
        radio3 = wx.RadioButton( panel, -1, "" )

        text1 = wx.TextCtrl( panel, -1, "Open" )
        text2 = wx.TextCtrl( panel, -1, "Close" )
        text3 = wx.TextCtrl( panel, -1, "" )

        self.group1_ctrls.append((radio1, text1))
        self.group1_ctrls.append((radio2, text2))
        self.group1_ctrls.append((radio3, text3))

        for radio, text in self.group1_ctrls:
            sizer3.Add( radio, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            sizer3.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        staticText1 = wx.StaticText(self, -1, "Resistance Coeff", pos=(25,25))

        spin = wx.SpinCtrlDouble(self, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin.SetDigits(2)

        # ADD EVERYTHING TO APPROPRIATE SIZER
        Sizer1.Add( box1, 1, wx.ALIGN_CENTRE|wx.ALL, 5 )
        box1.Add(combobox, 0, wx.ALIGN_LEFT|wx.ALL, 5 )
        box1.Add(sizer2, 1, wx.ALIGN_CENTRE|wx.ALL, 5 )
        box1.Add(sizer4, 1, wx.ALIGN_LEFT|wx.ALL, 5 )

        sizer2.Add(TextCtrl1, 0, wx.ALIGN_LEFT|wx.ALL, 5 )
        sizer2.Add(sizer3, 1, wx.ALIGN_LEFT|wx.ALL, 5 )

        sizer4.Add(staticText1, 1, wx.ALIGN_LEFT|wx.ALL, 5 )
        sizer4.Add(spin, 1, wx.ALIGN_LEFT|wx.ALL, 5 )


        panel.SetSizer( Sizer1 )
        Sizer1.Fit(panel)
        # panel.Move( (50,50) )

        # Setup event handling and initial state for controls:
        for radio, text in self.group1_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnGroup1Select, radio )

        for radio, text in self.group1_ctrls:
            radio.SetValue(0)
            text.Enable(False)

    def OnGroup1Select(self, event ):
        radio_selected = event.GetEventObject()

        for radio, text in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
            else:
                text.Enable(False)

    def OnGroup2Select(self, event ):
        radio_selected = event.GetEventObject()

        for radio, text in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
            else:
                text.Enable(False)


class ValveTabPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        self.SetBackgroundColour((202,223,244))
        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(ListPanel(self, None, data=nodedata), 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)

        sizer.Add(sizer2, 1, wx.ALL, 5)

        sizer2.Add(ValveInfoPanel(self), 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
        # sizer2.Add(changed name.NodePropertiesPanel(self), 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
        sizer2.Add(ValveMethodPanel(self),1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5 )
        self.SetSizerAndFit(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()

#####################################################################################################

class CompressorListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        rows = [("NN1", "Kadikoy", "1996")
                ]
        self.list_ctrl = EditableListCtrl(self, style=wx.LC_REPORT)

        self.list_ctrl.InsertColumn(1, "VALVE NO", width=70)
        self.list_ctrl.InsertColumn(1, "TITLE", width=100)
        self.list_ctrl.InsertColumn(1, "LABEL", width=60)


        index = 0
        for row in rows:
            self.list_ctrl.InsertStringItem(index, row[0])
            self.list_ctrl.SetStringItem(index, 1, row[1])
            self.list_ctrl.SetStringItem(index, 2, row[2])
            index += 1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.FIXED_MINSIZE|wx.ALIGN_LEFT|wx.TOP, 0)
        self.SetSizer(sizer)

class CompressorPhysicalPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        bmp = wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        button = wx.BitmapButton(self, -1, bmp, (20, 20),
                       (bmp.GetWidth(), bmp.GetHeight()))
        button.SetToolTipString("Coordinate Selection From Map")

        l1 = wx.StaticText(self, -1, "X COORD.")
        t1 = wx.TextCtrl(self, -1, "12346566", size=(80, -1))
        l2 = wx.StaticText(self, -1, "Y COORD.")
        t2 = wx.TextCtrl(self, -1, "12314566", size=(80, -1))
        l3 = wx.StaticText(self, -1, "ALTITUDE")
        t3 = wx.TextCtrl(self, -1, "1200", size=(80, -1))

        l4 = wx.StaticText(self, -1, "SUCTION DISTANCE:")
        t4 = wx.TextCtrl(self, -1, "2300", size=(80, -1))
        Suction_Distance_Choices = ['Km', 'Miles']
        Suction_Distance_Choice = wx.Choice(self, -1, size=(60, 50),choices = Suction_Distance_Choices)
        Suction_Distance_Choice.SetSelection(0)


        sizerphysical = wx.FlexGridSizer(rows=2, cols=2, hgap=0, vgap=1)
        sizerphysical1 = wx.FlexGridSizer(rows=3, cols=2, hgap=15, vgap=1)
        sizerphysical1.SetFlexibleDirection( wx.BOTH )
        sizerphysical1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sizerphysical1.AddMany([ l1, t1,
                        l2, t2,
                        l3, t3])

        sizerphysical2 = wx.BoxSizer(wx.VERTICAL)
        sizerphysical.Add(sizerphysical1, 1, wx.ALL|wx.EXPAND, 0)
        sizerphysical.Add(sizerphysical2, 1, wx.ALL, 0)
        sizerphysical2.Add(button, 1, wx.TOP|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizerphysical2.Add(AltUnitSingleChoice(self), 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        Bottom_Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Bottom_Sizer.Add(l4,0,wx.ALIGN_LEFT, 0)
        Bottom_Sizer.Add(t4,0,wx.ALIGN_LEFT, 0)
        Bottom_Sizer.Add(Suction_Distance_Choice,0,wx.ALIGN_LEFT, 0)

        sizer.Add(sizerphysical, 0, wx.ALL|wx.EXPAND | wx.ALIGN_BOTTOM, 5)
        sizer.Add(Bottom_Sizer, 0, wx.ALL | wx.EXPAND| wx.ALIGN_TOP, 5)


        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        sizerphysical.Fit(self)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, evt):
        if self.GetAutoLayout():
            self.Layout()


class CompressorInfoPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,180))

        self.staticText1 = wx.StaticText(self, -1, "CON. PIPE")
        self.staticText2 = wx.StaticText(self, -1, "SUCTION")
        self.staticText3 = wx.StaticText(self, -1, "DISCHARGE")
        self.staticText4 = wx.StaticText(self, -1, "COMMENT")

        self.staticText1ctrl1 = wx.TextCtrl(self, -1, "P123")
        self.staticText3ctrl2 = wx.TextCtrl(self, -1, "N32")
        self.staticText1ctrl3 = wx.TextCtrl(self, -1, "Comment")

        choices = [u"N2", u"Source Node", u"Junction Node", u"Wellhead"]
        self.choice1 = wx.Choice(self, -1, choices=choices)
        self.choice1.SetSelection(0)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        sizer1.Add(CompressorListPanel(self), 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer2, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer3, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer4, 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(CompressorPhysicalPanel(self), 1, wx.ALL|wx.EXPAND, 0)

        sizer2.Add(self.staticText1, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.staticText2, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.staticText3, 1, wx.ALL|wx.EXPAND, 5)

        sizer3.Add(self.staticText1ctrl1, 0, wx.ALL|wx.EXPAND, 5)
        sizer3.Add(self.choice1, 0, wx.ALL|wx.EXPAND, 5)
        sizer3.Add(self.staticText3ctrl2, 0, wx.ALL|wx.EXPAND, 5)

        sizer4.Add(self.staticText4, 0, wx.ALL|wx.EXPAND, 5)
        sizer4.Add(self.staticText1ctrl3, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer1)
        sizer1.Fit(self)
        # self.SetAutoLayout(1)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, evt):
        if self.GetAutoLayout():
            self.Layout()


class CompressorMethodPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)
        panel = wx.Panel(self, -1)

        box1_title = wx.StaticBox(panel, -1, "METHOD SELECTION" )
        box1 = wx.StaticBoxSizer(box1_title, wx.VERTICAL)

        box2_title = wx.StaticBox(panel, -1, "PROPERTIES & DESIGN" )
        box2 = wx.StaticBoxSizer(box2_title, wx.VERTICAL)

        topSizer = wx.BoxSizer(wx.VERTICAL)

        # sizers for box 1
        grid1 = wx.FlexGridSizer(rows=3, cols=4, hgap=0, vgap=0)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        # sizers for box 2
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)


        # controls for box 1
        sampleList = ['What am I doing right now, jesus christ', 'one', 'two', 'three', 'four', 'five',
                      #'this is a long item that needs a scrollbar...',
                      'six', 'seven', 'eight']

        comboBox = wx.ComboBox(panel, 500, "Choose Compressor Type", (90, 50),
                         (200, -1), sampleList,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )


        radio1 = wx.RadioButton( panel, -1, "", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "" )
        radio3 = wx.RadioButton( panel, -1, "" )
        radio4 = wx.RadioButton( panel, -1, "" )

        text1 = wx.TextCtrl( panel, -1, "Inlet Pressure" )
        text2 = wx.TextCtrl( panel, -1, "Outlet Pressure" )
        text3 = wx.TextCtrl( panel, -1, "Flow" )
        text4 = wx.TextCtrl( panel, -1, "Compression Ratio" )

        text12 = wx.TextCtrl( panel, -1, "2300" )
        text22 = wx.TextCtrl( panel, -1, "2300" )
        text32 = wx.TextCtrl( panel, -1, "2300" )

        units_list = ['Units', 'Meters', 'Feet']
        Unit_Choice1= wx.Choice(panel, -1, size=(60, 50),choices = units_list)
        Unit_Choice1.SetSelection(0)
        Unit_Choice2= wx.Choice(panel, -1, size=(60, 50),choices = units_list)
        Unit_Choice2.SetSelection(0)
        Unit_Choice3= wx.Choice(panel, -1, size=(60, 50),choices = units_list)
        Unit_Choice3.SetSelection(0)

        spin1 = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin1.SetDigits(2)

        # controls for box 2 #################
        button1 = wx.Button(panel, 10, "Typical Comp/ C. Station Design", (20, 20))
        button1.SetDefault()
        button1.SetSize(button1.GetBestSize())

        spin2 = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin2.SetDigits(2)

        spin3 = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin3.SetDigits(2)

        spin4 = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin4.SetDigits(2)

        StaticText1 = wx.StaticText(panel, -1, "No. of Serial Compressors")
        StaticText2 = wx.StaticText(panel, -1, "Poly Eff.")
        StaticText3 = wx.StaticText(panel, -1, "Com Eff")
        StaticText4 = wx.StaticText(panel, -1, "Suction Temp")

        text5 = wx.TextCtrl(panel, -1, "2300")

        Unit_Choice4 = wx.Choice(panel, -1, size=(60, 50),choices = units_list)
        Unit_Choice4.SetSelection(0)

        # making flex grid for method selection
        grid1.Add(radio1, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text1, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text12, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(Unit_Choice1, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(radio2, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text2, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text22, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(Unit_Choice2, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(radio3, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text3, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(text32, 0, wx.ALIGN_LEFT|wx.ALL)
        grid1.Add(Unit_Choice3, 0, wx.ALIGN_LEFT|wx.ALL)

        # Add static box sizers to panel sizer
        topSizer.Add(box1, 1, wx.ALIGN_LEFT)
        topSizer.Add(box2, 1, wx.ALIGN_LEFT)

        # Box 1
        box1.Add(comboBox, 0, wx.ALIGN_LEFT)
        box1.Add(grid1, 0, wx.ALIGN_LEFT)
        box1.Add(sizer3, 0, wx.ALIGN_LEFT)

        sizer3.Add(radio4, 0, wx.ALIGN_LEFT)
        sizer3.Add(text4, 0, wx.ALIGN_LEFT)
        sizer3.Add(spin1, 0, wx.ALIGN_LEFT)

        # Box 2
        box2.Add(sizer4, 1, wx.ALIGN_LEFT)
        box2.Add(sizer5, 1, wx.ALIGN_LEFT)
        box2.Add(sizer6, 1, wx.ALIGN_LEFT)
        box2.Add(button1, 1, wx.ALIGN_CENTRE)

        sizer4.Add(StaticText1, 0, wx.ALIGN_LEFT)
        sizer4.Add(spin2, 0, wx.ALIGN_LEFT)

        sizer5.Add(StaticText2, 0, wx.ALIGN_LEFT)
        sizer5.Add(spin3, 0, wx.ALIGN_LEFT)
        sizer5.Add(StaticText3, 0, wx.ALIGN_LEFT)
        sizer5.Add(spin4, 0, wx.ALIGN_LEFT)

        sizer6.Add(StaticText4, 0, wx.ALIGN_LEFT)
        sizer6.Add(text5, 0, wx.ALIGN_LEFT)
        sizer6.Add(Unit_Choice4, 0, wx.ALIGN_LEFT)

        panel.SetSizer(topSizer)
        topSizer.Fit(panel)

class CompressorTabPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        self.SetBackgroundColour((202,223,244))
        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(ListPanel(self, None, data=nodedata), 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)

        sizer.Add(sizer2, 1, wx.ALL, 5)

        sizer2.Add(CompressorInfoPanel(self), 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
        sizer2.Add(CompressorMethodPanel(self),1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5 )
        self.SetSizerAndFit(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()

##################################################################################
class PipeListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        rows = [("NN1", "Kadikoy", "1996")
                ]
        self.list_ctrl = EditableListCtrl(self, style=wx.LC_REPORT)

        self.list_ctrl.InsertColumn(1, "PIPE NO", width=70)
        self.list_ctrl.InsertColumn(1, "TITLE", width=100)
        self.list_ctrl.InsertColumn(1, "LABEL", width=60)


        index = 0
        for row in rows:
            self.list_ctrl.InsertStringItem(index, row[0])
            self.list_ctrl.SetStringItem(index, 1, row[1])
            self.list_ctrl.SetStringItem(index, 2, row[2])
            index += 1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL|wx.FIXED_MINSIZE|wx.ALIGN_LEFT|wx.TOP, 0)
        self.SetSizer(sizer)

class PipeInfoPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""

        wx.Panel.__init__(self, parent, -1)
        panel = wx.Panel(self, -1)

        # sizers

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer7 = wx.BoxSizer(wx.HORIZONTAL)

        # controls

        staticText1 = wx.StaticText(panel, -1, "FROM")
        staticText2 = wx.StaticText(panel, -1, "TO")
        staticText3 = wx.StaticText(panel, -1, "COMMENT")
        staticText4 = wx.StaticText(panel, -1, "LENGTH")

        bmp1 = wx.Image("aquabutton.jpg", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp1, wx.BLUE)
        bmp1.SetMask(mask)
        bmpButton1 = wx.BitmapButton(self, -1, bmp1, (20, 20),
                       (bmp1.GetWidth(), bmp1.GetHeight()))

        bmp2 = wx.Image("aquabutton.jpg", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp2, wx.BLUE)
        bmp2.SetMask(mask)
        bmpButton2 = wx.BitmapButton(self, -1, bmp2, (20, 20),
                       (bmp2.GetWidth(), bmp2.GetHeight()))

        bmp3 = wx.Image("aquabutton.jpg", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp3, wx.BLUE)
        bmp3.SetMask(mask)
        bmpButton3 = wx.BitmapButton(self, -1, bmp3, (20, 20),
                       (bmp3.GetWidth(), bmp3.GetHeight()))
        # Maybe you want to give it a string later
        # button.SetToolTipString("Coordinate Selection From Map")

        t1 = wx.TextCtrl(panel, -1, "N123", size=(125, -1))
        t2 = wx.TextCtrl(panel, -1, "N12", size=(125, -1))
        t3 = wx.TextCtrl(panel, -1, "Comment", style=wx.TE_MULTILINE)
        t4 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))
        t5 = wx.TextCtrl(panel, -1, "23", size=(125, -1))
        t6 = wx.TextCtrl(panel, -1, "0.1", size=(125, -1))

        rButton1 = wx.RadioButton(panel, -1, "Standard Dia." )
        rButton2 = wx.RadioButton(panel, -1, "Inner Dia." )
        rButton3 = wx.RadioButton(panel, -1, "Thickness" )

        choices1 = [u"Km", u"Mile"]
        choices2 = [u"Choose", u"Choose Life", u"Choose a Jb", u"Choose a Career",  u"Choose a Family", u"Choose a Fucking Big Television"]
        choices3 = [u"Meter", u"Feet"]

        choice1 = wx.Choice(panel, -1, choices=choices1)
        choice1.SetSelection(0)
        choice2 = wx.Choice(panel, -1, choices=choices2)
        choice2.SetSelection(0)
        choice3 = wx.Choice(panel, -1, choices=choices3)
        choice3.SetSelection(0)
        choice4 = wx.Choice(panel, -1, choices=choices3)
        choice4.SetSelection(0)

        button1 = wx.Button(panel, 10, "Material Properties", (20, 20))

        # adding everything to their respective sizer
        sizer1.Add(PipeListPanel(self), 0, wx.ALL|wx.EXPAND, 5)
        sizer1.Add(sizer2, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(sizer3, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(sizer4, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(sizer5, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(sizer6, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(sizer7, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(button1, 0,  wx.ALIGN_CENTRE | wx.ALL|wx.EXPAND, 5)

        sizer2.Add(staticText1, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(t1, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(bmpButton1, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(staticText2, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(t2, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(bmpButton2, 0, wx.ALL | wx.EXPAND, 5)

        sizer3.Add(staticText3, 0, wx.ALL | wx.EXPAND, 5)
        sizer3.Add(t3, 1, wx.ALL | wx.EXPAND, 5)

        sizer4.Add(staticText4, 0, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(t4, 0, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(choice1, 0, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(bmpButton3, 0, wx.ALL | wx.EXPAND, 5)

        sizer5.Add(rButton1, 0, wx.ALL | wx.EXPAND, 5)
        sizer5.Add(choice2, 0, wx.ALL | wx.EXPAND, 5)

        sizer6.Add(rButton2, 0, wx.ALL | wx.EXPAND, 5)
        sizer6.Add(t5, 0, wx.ALL | wx.EXPAND, 5)
        sizer6.Add(choice3, 0, wx.ALL | wx.EXPAND, 5)

        sizer7.Add(rButton3, 0, wx.ALL | wx.EXPAND, 5)
        sizer7.Add(t6, 0, wx.ALL | wx.EXPAND, 5)
        sizer7.Add(choice4, 0, wx.ALL | wx.EXPAND, 5)

        # set the top sizer and fit to min size/layout
        panel.SetSizer(sizer1)
        sizer1.Fit(panel)

class PipeMethodPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)

        panel = wx.Panel(self, -1)

        ################# CONTROLS FIRST STATIC BOX
        box1 = wx.StaticBox(panel, -1, "METHOD SELECTION")
        box2 = wx.StaticBox(panel, -1, "AMBIENT")

        sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
                      #'this is a long item that needs a scrollbar...',
                      'six', 'seven', 'eight']

        combo = wx.ComboBox(panel, 500, "Choose Pipe Equation", (90, 50),
                         (160, -1), sampleList,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )

        t1 = wx.TextCtrl(panel, -1, "Pipe Eff.", size=(125, -1))
        t2 = wx.TextCtrl(panel, -1, "Roughness", size=(125, -1))
        t3 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))
        t4 = wx.TextCtrl(panel, -1, "Friction Factor", size=(125, -1))
        t5 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))
        t6 = wx.TextCtrl(panel, -1, "Base Temp", size=(125, -1))
        t7 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))

        spin = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(80,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin.SetDigits(2)

        choices1 = [u"Unit", u"Books and Such"]
        choices2 = [u"Celsius", u"Fahrenheit"]

        choice1 = wx.Choice(panel, -1, choices=choices1)
        choice1.SetSelection(0)

        choice2 = wx.Choice(panel, -1, choices=choices1)
        choice2.SetSelection(0)

        choice3 = wx.Choice(panel, -1, choices=choices2)
        choice3.SetSelection(0)

        ################# CONTROLS SECOND STATIC BOX #################
        rButton1 = wx.RadioButton(panel, -1, "Sim Def." )
        rButton2 = wx.RadioButton(panel, -1, "User Def." )

        t8 = wx.TextCtrl(panel, -1, "Amb. Pres.", size=(125, -1))
        t9 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))
        t10 = wx.TextCtrl(panel, -1, "Amb. Temp.", size=(125, -1))
        t11 = wx.TextCtrl(panel, -1, "2300", size=(125, -1))

        choices3 = [u"KPa", u"PSI"]

        choice4 = wx.Choice(panel, -1, choices=choices3)
        choice4.SetSelection(0)

        choice5 = wx.Choice(panel, -1, choices=choices2)
        choice5.SetSelection(0)

        ################ SIZERS FIRST STATIC BOX ###############
        # SIZERS
        topsizer = wx.BoxSizer(wx.VERTICAL)
        staticSizer1 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        staticSizer2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)

        # ADD CONTROLS TO APPROPRIATE SIZERS
        topsizer.Add(staticSizer1, 1, wx.EXPAND|wx.ALL, 5)
        topsizer.Add(staticSizer2, 1, wx.EXPAND|wx.ALL, 5)

        staticSizer1.Add(combo, 0, wx.EXPAND|wx.ALL, 5)
        staticSizer1.Add(sizer3, 0, wx.EXPAND|wx.ALL, 5)
        staticSizer1.Add(sizer4, 0, wx.EXPAND|wx.ALL, 5)
        staticSizer1.Add(sizer5, 0, wx.EXPAND|wx.ALL, 5)
        staticSizer1.Add(sizer6, 0, wx.EXPAND|wx.ALL, 5)

        sizer3.Add(t1, 0, wx.EXPAND|wx.ALL, 5)
        sizer3.Add(spin, 0, wx.EXPAND|wx.ALL, 5)

        sizer4.Add(t2,0, wx.EXPAND|wx.ALL, 0)
        sizer4.Add(t3,0, wx.EXPAND|wx.ALL, 0)
        sizer4.Add(choice1, 0, wx.EXPAND|wx.ALL, 0)

        sizer5.Add(t4, 0, wx.EXPAND|wx.ALL, 0)
        sizer5.Add(t5, 0, wx.EXPAND|wx.ALL, 0)
        sizer5.Add(choice2, 0, wx.EXPAND|wx.ALL, 0)

        sizer6.Add(t6, 0, wx.EXPAND|wx.ALL, 0)
        sizer6.Add(t7, 0, wx.EXPAND|wx.ALL, 0)
        sizer6.Add(choice3, 0, wx.EXPAND|wx.ALL, 0)

        ################ SIZERS SECOND STATIC BOX ###############

        sizer7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer9 = wx.BoxSizer(wx.HORIZONTAL)

        staticSizer2.Add(sizer7, 1, wx.EXPAND|wx.ALL, 10)
        staticSizer2.Add(sizer8, 1, wx.EXPAND|wx.ALL, 10)
        staticSizer2.Add(sizer9, 1, wx.EXPAND|wx.ALL, 10)

        sizer7.Add(rButton1, 1, wx.EXPAND|wx.ALL, 10)
        sizer7.Add(rButton2, 1, wx.EXPAND|wx.ALL, 10)

        sizer8.Add(t8, 0, wx.EXPAND|wx.ALL, 0)
        sizer8.Add(t9, 0, wx.EXPAND|wx.ALL, 0)
        sizer8.Add(choice4, 0, wx.EXPAND|wx.ALL, 0)

        sizer9.Add(t10, 0, wx.EXPAND|wx.ALL, 0)
        sizer9.Add(t11, 0, wx.EXPAND|wx.ALL, 0)
        sizer9.Add(choice5, 0, wx.EXPAND|wx.ALL, 0)

        #####################################

        panel.SetSizer(topsizer)
        topsizer.Fit(panel)

class PipeTabPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.SetBackgroundColour((202,223,244))

        self.panel1 = PipeInfoPanel(self)
        self.panel2 = PipeMethodPanel(self)

        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]

        sizer1 = wx.BoxSizer(wx.VERTICAL)

        sizer1.Add(ListPanel(self, None, data=nodedata), 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)
        sizer1.Add(self.panel1, 1, wx.EXPAND | wx.ALL, 0)
        sizer1.Add(self.panel2, 1, wx.EXPAND | wx.ALL, 0)

        self.SetSizerAndFit(sizer1)
        #sizer1.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

'''LEFT MENU MAIN CLASS (NOTEBOOK)'''
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
        # Create the first tab and add it to the notebook
        tabOne = NodeTabPanel(self)
        tabOne.SetBackgroundColour((202,223,244))
        self.AddPage(tabOne, "ND")

        # Show how to put an image on one of the notebook tabs,
        # first make the image list:
        il = wx.ImageList(16, 16)
        idx1 = il.Add(images.Smiles.GetBitmap())
        self.AssignImageList(il)

        # now put an image on the first tab we just created:
        self.SetPageImage(0, idx1)

        # Create and add the second tab
        tabTwo = PipeTabPanel(self)
        self.AddPage(tabTwo, "PP")

        self.AddPage(ValveTabPanel(self), "VV")
        self.AddPage(CompressorTabPanel(self), "CP")
        self.AddPage(NodeTabPanel(self), "RG")
        self.AddPage(NodeTabPanel(self), "LE")
        self.AddPage(NodeTabPanel(self), "HC")
        self.AddPage(NodeTabPanel(self), "LS")


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

        # DRAWING FRAMEWORK AND PANEL
        self.graph = PypeGraph.Graph()
        self.drawing_canvas = GDP.GraphDesignPanel(panel, self.graph)

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

        #########################################################################################################
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

        #########################################################################################################
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

        Images_Group.AddSimpleButton(wx.ID_ANY, "General Settings", options_bmp1,
                                  "This is a tooltip for adding Nodes")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Display / Labeling Settings", options_bmp2,
                                  "This is a tooltip for adding Valves")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Unit Settings", options_bmp3,
                                  "This is a tooltip for adding Compressors")
        Images_Group.AddSimpleButton(wx.ID_ANY, "Short-Cut Settings", options_bmp4,
                                  "This is a tooltip for adding Regulators")

        #########################################################################################################

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
        bmp8= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp9= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp10= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp11= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        bmp12= wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        # PANELS IN DESIGN RIBBON PAGE
        _Element_Add = RB.RibbonPanel(Design, wx.ID_ANY, "Add Element", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_General = RB.RibbonPanel(Design, wx.ID_ANY, "Design General", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Design_View = RB.RibbonPanel(Design, wx.ID_ANY, "Design View", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        _Zoom_Panel = RB.RibbonPanel(Design, wx.ID_ANY, "Design View", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        # OGUZ = RB.RibbonPanel(Design, wx.ID_ANY, "OGUZ", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))
        # _Coordinate = RB.RibbonPanel(Design, wx.ID_ANY, "Coordinate", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        # "BUTTON BARS" OF EACH PANEL IN DESIGN PAGE
        drawing_tools = RB.RibbonButtonBar(_Element_Add)
        viewing_tools = RB.RibbonButtonBar(_Design_View)
        general_tools = RB.RibbonButtonBar(_Design_General)
        # drawing_tools = RB.RibbonButtonBar(_Element_Add)
        # drawing_tools = RB.RibbonButtonBar(_Element_Add)

        # ADDING BUTTONS TO RESPECTIVE BUTTON BAR
        drawing_tools.AddSimpleButton(wx.ID_ANY, "Nodes", bmp1,
                                  "This is a tooltip for adding Nodes")
        drawing_tools.AddSimpleButton(wx.ID_ANY, "Valves", bmp2,
                                  "This is a tooltip for adding Valves")
        drawing_tools.AddSimpleButton(wx.ID_ANY, "Compressors", bmp3,
                                  "This is a tooltip for adding Compressors")
        drawing_tools.AddSimpleButton(wx.ID_ANY, "Regulators", bmp4,
                                  "This is a tooltip for adding Regulators")
        drawing_tools.AddSimpleButton(wx.ID_ANY, "Loss Elements", bmp5,
                                  "This is a tooltip for adding Loss Elements")


        viewing_tools.AddSimpleButton(wx.ID_ANY, "Zoom In", Resources.getMagPlusBitmap(),
                                  "This is a tooltip for zooming")
        viewing_tools.AddSimpleButton(wx.ID_ANY, "Zoom Out", Resources.getMagMinusBitmap(),
                                  "This is a tooltip for zooming out")
        viewing_tools.AddSimpleButton(wx.ID_ANY, "Panning", Resources.getHandBitmap(),
                                  "This is a tooltip for panning")
        # Make scale a text control, not a button
        # wx.TextCtrl( panel, -1, "Open" )
        viewing_tools.AddSimpleButton(wx.ID_ANY, "Scale", bmp6,
                                  "This is a tooltip to show the zoom percentage ")
        viewing_tools.AddSimpleButton(wx.ID_ANY, "Map", bmp7,
                                  "This is a tooltip to display the embedded map")


        general_tools.AddSimpleButton(wx.ID_ANY, "Element Selection Tool", bmp8,
                                  "This is a tooltip for selecting")
        general_tools.AddSimpleButton(wx.ID_ANY, "Drag", bmp9,
                                  "This is a tooltip for dragging elements")
        general_tools.AddSimpleButton(wx.ID_ANY, "Delete", bmp10,
                                  "This is a tooltip for deleting elements")
        general_tools.AddSimpleButton(wx.ID_ANY, "Undo", bmp11,
                                  "This is a tooltip to undo")
        general_tools.AddSimpleButton(wx.ID_ANY, "Redo", bmp12,
                                  "This is a tooltip to redo")

        Zoom_Text = wx.StaticText(_Zoom_Panel, -1, "Percentage Zoomed", (20, 120))
        Zoom_Text.SetBackgroundColour(wx.Colour(255, 251, 204))

        zoom_text_control = wx.TextCtrl(_Zoom_Panel, -1, "2300", size=(125, -1))

        # ADD SIZER TO PANEL
        Zoom_sizer = wx.BoxSizer(wx.VERTICAL)
        Zoom_sizer.AddStretchSpacer(1)

        # ADD CONTROLS TO SIZER
        Zoom_sizer.Add(Zoom_Text, 4, wx.ALL|wx.EXPAND, 2)
        Zoom_sizer.Add(zoom_text_control, 0, wx.ALL|wx.EXPAND, 2)
        _Zoom_Panel.SetSizer(Zoom_sizer)

        #######################################################################

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
        sim_bmp1 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp2 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp3 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp4 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp5 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp6 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        sim_bmp7 = wx.Image("design.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

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

        #######################################################################
        #######################################################################
        #######################################################################

        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self._bitmap_creation_dc.SetFont(label_font)

        # Now instantiate all of them
        self._ribbon.Realize()

        ############################################################################

        # We added NotebookDemo for left side screen, testauipanel for design screen, testsearchcontrol for search buton
        self.notebook = Notebook(panel)


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
        self.BindEvents([toolbar_panel, _Element_Add])
        '''WE NEED TO ORGINIZED WAY PUTTING ALL THE IMAGES IN'''

        self.SetIcon(images.Mondrian.Icon)

        self.CenterOnScreen()
        self.Show()

    # FOR USE WITH FILE MENU BAR
    def OnQuit(self, e):
        self.Close()

    def BindEvents(self, bars):

        # SYNTAX:
        # ribbon_page_panel.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnDefaultProvider, id)

        design_bar, toolbar_panel = bars

        design_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnDrawingPanelClick, id=-1)


    def OnDrawingPanelClick(self, event):
        pass


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
    frame = RibbonFrame(None, -1, "PypeSim @ASRAD",size=(900, 500))
    frame.Show(True)
    frame.Centre()
    app.MainLoop()
