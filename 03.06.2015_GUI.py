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
import UIGraph as UIG


import overlay_alpha

>>>>>>> ea11b89ebdc523f6b6d8561527d99b5bdb336c5d:03.06.2015_GUI.py


########################################################################

'''ERROR TESTING'''

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])


########################################################################

'''GENERAL BITMAP FUNCTION TO SAVE US THE PAIN OF WRITING IT EACH TIME'''

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

        # Layout controls on panel:

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

        # Layout controls on panel:

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

class NodeTabPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

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

        self.SetSizer(sizer)

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
        tabTwo = NodeTabPanel(self)
        tabTwo.SetBackgroundColour((202,223,244))
        self.AddPage(tabTwo, "PP")

        # Create and add the third tab
        tabThree = NodeTabPanel(self)
        tabThree.SetBackgroundColour((202,223,244))
        self.AddPage(tabThree, "GG")

        self.AddPage(NodeTabPanel(self), "VV")
        self.AddPage(NodeTabPanel(self), "CP")
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

'''RIBBON SECTION'''
'''For every functionality panel within the ribbon toolbar... create panel and corresponding sizer'''

class RibbonFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, log=None):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # menubar = wx.MenuBar()
        # fileMenu = wx.Menu()
        # fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        # menubar.Append(fileMenu, '&File')
        # self.SetMenuBar(menubar)

        # self.toolbar = self.CreateToolBar()
        # self.toolbar.AddLabelTool(1, '', wx.Bitmap("aquabutton.jpg"))
        # self.toolbar.Realize()

        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

        panel = scrolled.ScrolledPanel(self)
        #NOTE
        # in init assign wx.lib.agw.ribbon.RibbonBar after which you can add pages to with wx.lib.agw.ribbon.RibbonPage
        self._ribbon = RB.RibbonBar(panel, wx.ID_ANY, agwStyle=RB.RIBBON_BAR_DEFAULT_STYLE|RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)


        '''LOOK AT WHERE THE MEMORY DC IS BEING PUT INTO PAINT DC LATER'''

        self._bitmap_creation_dc = wx.MemoryDC()
        self._colour_data = wx.ColourData()
        # self._ribbon.GetArtProvider().SetColourScheme(1, 1, 1)
        # self._colour_data.SetColour('80FFAA')


        '''RIBBON PAGE CREATION'''


        File = RB.RibbonPage(self._ribbon, wx.ID_ANY, "FILE")
        Options = RB.RibbonPage(self._ribbon, wx.ID_ANY, "OPTIONS")
        Layout = RB.RibbonPage(self._ribbon, wx.ID_ANY, "LAYOUT")
        Design = RB.RibbonPage(self._ribbon, wx.ID_ANY, "DESIGN")
        Simulation = RB.RibbonPage(self._ribbon, wx.ID_ANY, "SIMULATION")
        Results = RB.RibbonPage(self._ribbon, wx.ID_ANY, "RESULTS")
        Help = RB.RibbonPage(self._ribbon, wx.ID_ANY, "HELP")

        '''FILE PANEL SETTINGS'''

        toolbar_panel = RB.RibbonPanel(File, wx.ID_ANY, "", wx.NullBitmap, wx.DefaultPosition,
                                       wx.DefaultSize, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE|RB.RIBBON_PANEL_EXT_BUTTON)

        # The panel that the Ribbon toolbar takes has to be called wx.lib.agw.ribbon.RibbonPanel
        # Can create toolbar as wx.lib.agw.ribbon.Toolbar(wx.lib.agw.ribbon.RibbonPanel, id)

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

        #######################################################################

        # DESIGN RIBBON PANELS
        # PANELS ORGANIZED TO BY FUNCTION
        # FIRST PANEL HOLDS DRAWING FUNCTIONS

        # Just testing
        bmp= wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        design_bar = RB.RibbonPanel(Design, wx.ID_ANY, "Drawing Tools", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        drawing_tools = RB.RibbonButtonBar(design_bar)

        drawing_tools.AddSimpleButton(wx.ID_ANY, "Line Tool", bmp,
                                  "This is a tooltip for line drawing")

        drawing_tools.AddSimpleButton(wx.ID_ANY, "Node Tool", bmp,
                                  "This is a tooltip for adding nodes")

        # SECOND PANEL HOLDS VIEWING FUNCTIONS
        # VIEWING ICONS ARE TAKEN FROM FLOATCANVAS RESOURCES
        view_bar = RB.RibbonPanel(Design, wx.ID_ANY, "View", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(24, 23)))

        viewing_tools = RB.RibbonButtonBar(view_bar)

        viewing_tools.AddSimpleButton(wx.ID_ANY, "Pointer", Resources.getPointerBitmap(),
                                  "This is a tooltip for hit testing lines")

        viewing_tools.AddSimpleButton(wx.ID_ANY, "Zoom In", Resources.getMagPlusBitmap(),
                                  "This is a tooltip for zooming")

        viewing_tools.AddSimpleButton(wx.ID_ANY, "Zoom Out", Resources.getMagMinusBitmap(),
                                  "This is a tooltip for zooming out")

        viewing_tools.AddSimpleButton(wx.ID_ANY, "Panning", Resources.getHandBitmap(),
                                  "This is a tooltip for panning")

        #######################################################################


        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self._bitmap_creation_dc.SetFont(label_font)

        # Now instantiate all of them
        self._ribbon.Realize()


        ############################################################################

        # We added NotebookDemo for left side screen, testauipanel for design screen, testsearchcontrol for search buton
        self.notebook = Notebook(panel)

        self.drawing_canvas = UIG.GraphDesignPanel(panel)

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
        self.BindEvents([toolbar_panel, design_bar])
        '''WE NEED TO ORGINIZED WAY PUTTING ALL THE IMAGES IN'''

        self.SetIcon(images.Mondrian.Icon)

        self.CenterOnScreen()
        self.Show()

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
