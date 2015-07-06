from __future__ import division

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.mixins.listctrl as listmix
import wx.dataview as dv

import ListCtrl



#################################################################
'''LIST PANEL'''

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
            node = self.data[row][1]
            message = "Are you sure you want to delete '" + node + "'"
            decision = wx.MessageBox(message, 'Deletion Warning!', wx.OK | wx.CANCEL)
            print decision
            if decision == wx.OK:
                # remove it from our data structure
                del self.data[row]
                # notify the view(s) using this model that it has been removed
                self.RowDeleted(row)
                ##Notify the user that the Row was deleted
                message = "'" + node + "' Deleted"
                wx.MessageBox(message, 'Delete Information',wx.OK)
            ##otherwise notify the user that the row is safe and sound
            else:
                message = "Deletion cancelled!"
                wx.MessageBox(message, 'Delete Information',wx.OK)


    def AddRow(self, value):
        # update data structure
        self.data.append(value)
        # notify views
        self.RowAppended()

class ListPanel(wx.Panel):


    def __init__(self, parent, model=None, data=None):
        wx.Panel.__init__(self, parent, -1,size=(250,230))

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
        self.dvc.AppendTextColumn("Type",   2, width=43, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Label",   3, width=45,  mode=dv.DATAVIEW_CELL_EDITABLE)

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
        b1 = wx.Button(self, label="View",size=(40,23), name="newView")
        self.Bind(wx.EVT_BUTTON, self.OnNewView, b1)
        b2 = wx.Button(self, label="Add Node",size=(65,23))
        self.Bind(wx.EVT_BUTTON, self.OnAddRow, b2)
        b3 = wx.Button(self, label="Del Node",size=(65,23))
        self.Bind(wx.EVT_BUTTON, self.OnDeleteRows, b3)

        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(b1, 0, wx.LEFT|wx.RIGHT, 12)
        btnbox.Add(b2, 0, wx.LEFT|wx.RIGHT, 12)
        btnbox.Add(b3, 0, wx.LEFT, 12)
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
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(240,50), style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

#################################################################
'''INFO PANEL'''

class NodeInfoPanel(wx.Panel):

    def __init__(self, parent):

        # NEED TO SEE IF STATIC SIZING IS AFFECTING OVERALL FITTING
        wx.Panel.__init__(self, parent, -1,size=(240,150))

        panel = wx.Panel(self, -1)

        # CONTROLS
        rows = [("1", "Kadikoy", "1996")]
        list_ctrl1 = EditableListCtrl(panel, style=wx.LC_REPORT)

        list_ctrl1.InsertColumn(0, "NODE NO", width=65)
        list_ctrl1.InsertColumn(1, "TITLE", width=110)
        list_ctrl1.InsertColumn(2, "LABEL", width=65)

        index = 0
        for row in rows:
            list_ctrl1.InsertStringItem(index, row[0])
            list_ctrl1.SetStringItem(index, 1, row[1])
            list_ctrl1.SetStringItem(index, 2, row[2])
            index += 1


        text1 = wx.StaticText(panel, -1, "LINKS :")
        text2 = wx.StaticText(panel, -1, "COMMENT :")
        text3 = wx.StaticText(panel, -1, "TYPE :")

        tctrl1 = wx.TextCtrl(panel, -1, "PP3 PP232 PP34543")
        tctrl2 = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)

        node_choices = [u"Demand Node",u"Source Node", u"Wellhead"]
        choices1 = wx.Choice(panel, wx.ID_ANY, choices=node_choices)
        choices1.SetSelection(0)

        # MAKE SIZERS
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        # ADD SIZERS APPROPRIATELY
        sizer1.Add(list_ctrl1, 0, wx.ALL|wx.EXPAND, 1)
        sizer1.Add(sizer2, 0, wx.ALL|wx.EXPAND, 1)
        sizer1.Add(sizer3, 0, wx.ALL|wx.EXPAND, 1)
        sizer1.Add(sizer4, 0, wx.ALL|wx.EXPAND, 1)

        sizer2.Add(text1, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer2.Add(tctrl1, 2, wx.ALL|wx.EXPAND, 1)

        sizer3.Add(text2, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer3.Add(tctrl2, 2, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 1)

        sizer4.Add(text3, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer4.Add(choices1, 2, wx.ALL|wx.EXPAND, 1)

        panel.SetSizer(sizer1)
        panel.SetAutoLayout(1)
        sizer1.Fit(panel)

#################################################################
'''PHYSICAL PANEL'''

class NodePhysicalPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        altitudeunitlist = ['Meters', 'Feet']

        self.ch = wx.Choice(self, -1, size=(60, -1),choices = altitudeunitlist)
        self.ch.SetSelection(0)


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
        sizerphysical2.Add(self.ch, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)


        sizer.Add(sizerphysical, 1, wx.ALL|wx.EXPAND, 5)


        self.SetSizer(sizer)
        sizerphysical.Fit(self)

#################################################################
'''PROPERTIES PANEL'''
'''PROPERTIES PANEL'''

class NodeMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # CONTROLS:

        flowunitlist = ['m3/s', 'ft3/s']
        flowunit_choice = wx.Choice(panel, -1, size=(60, -1),choices = flowunitlist)
        flowunit_choice.SetSelection(0)

        presunitlist = ['KPa', 'Pa', 'atm', 'Psi','bar']
        presunit_choice = wx.Choice(panel, -1, size=(60, -1),choices = presunitlist)
        presunit_choice.SetSelection(0)

        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox( panel, -1, "METHOD SELECTION" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=3 )

        # 1st group of controls:
        self.group1_ctrls = []
        radio1 = wx.RadioButton( panel, -1, "Non", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "Flow" )
        radio3 = wx.RadioButton( panel, -1, "Pressure " )
        text1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )
        text2 = wx.TextCtrl( panel, -1, "",size=(70, -1 ))
        text3 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        unit1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )

        self.group1_ctrls.append((radio1, text1, unit1))
        self.group1_ctrls.append((radio2, text2, flowunit_choice))
        self.group1_ctrls.append((radio3, text3, presunit_choice))

        for radio, text, unit in self.group1_ctrls:
            grid1.Add( radio, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (0,10) )

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
class NodeTempMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # CONTROLS:

        temp_unit_list = ['Kelv', 'Celc', 'Rank']
        temp_unit_choice = wx.Choice(panel, -1, size=(60, -1),choices = temp_unit_list)
        temp_unit_choice.SetSelection(0)

        vs = wx.BoxSizer(wx.VERTICAL)

        box1_title = wx.StaticBox(panel, -1, "TEMPERATURE OPTIONS" )
        box2 = wx.StaticBoxSizer(box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer(cols=3 )

        # 1st group of controls:
        self.group1_ctrls = []
        radio1 = wx.RadioButton( panel, -1, "Sim. Def.", style = wx.RB_GROUP )
        radio2 = wx.RadioButton( panel, -1, "User Def." )
        text1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )
        text2 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        unit1 = wx.StaticText( panel, -1, "",size=(10, -1 ) )

        self.group1_ctrls.append((radio1, text1, unit1))
        self.group1_ctrls.append((radio2, text2, temp_unit_choice))

        for radio, text, unit in self.group1_ctrls:
            grid1.Add( radio, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box2.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box2, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

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
class WellheadMethodRadioPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1 )

        panel = wx.Panel(self, -1 )

        # Layout controls on panel:

        vs = wx.BoxSizer(wx.VERTICAL)
        presunitlist = ['KPa', 'Pa', 'atm', 'Psi','bar']

        presunit_choice = wx.Choice(panel, -1, size=(60, -1),choices = presunitlist)
        presunit_choice.SetSelection(0)

        spin = wx.SpinCtrlDouble(panel, value='0.95', size=(70,-1),style=wx.SP_ARROW_KEYS,
                                 min=0.50, max=0.99, inc=0.01)
        spin.SetDigits(2)

        box1_title = wx.StaticBox( panel, -1, "WELLHEAD INPUT" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer(cols=3)

        # 1st group of controls:
        self.group1_ctrls = []
        text1 = wx.StaticText( panel, -1, "Cut-Off Pres.",size=(70, -1 ) )
        text2 = wx.StaticText( panel, -1, "Exponent",size=(70, -1 ) )
        input1 = wx.TextCtrl( panel, -1, "",size=(70, -1 ) )
        empty_static_text = wx.StaticText( panel, -1, "",size=(10, -1 ) )

        self.group1_ctrls.append((text1, input1, presunit_choice))
        self.group1_ctrls.append((text2, spin, empty_static_text))

        for title, text, unit in self.group1_ctrls:
            grid1.Add( title, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
            grid1.Add( unit, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 1)

        panel.SetSizer( vs )
        vs.Fit( panel )
        panel.Move( (0,10) )
class NodePropertiesPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,100))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(NodeMethodRadioPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(NodeTempMethodRadioPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(WellheadMethodRadioPanel(self), 0, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)

#################################################################
'''NODE TAB SECTION'''

class NodeTabPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        primary = wx.Colour(204, 204, 204, 150)
        self.SetBackgroundColour(primary)

        nodedata = ListCtrl.nodedata.items()
        nodedata.sort()
        nodedata = [[str(k)] + list(v) for k,v in nodedata]

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(ListPanel(self, None, data=nodedata), 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 5)
        sizer.Add(NodeInfoPanel(self), 0, wx.TOP|wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 5)
        sizer.Add(NodePhysicalPanel(self), 0, wx.TOP| wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 10)
        sizer.Add(NodePropertiesPanel(self), 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 15)

        self.SetSizerAndFit(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()


#################################################################################################################
#################################################################################################################
#################################################################################################################


SCREEN_WIDTH = 300
SCREEN_HEIGHT = 1000

class WhereTheRibbonWillGo(wx.Frame):
    def __init__(self, parent, id, title, position, size):
        wx.Frame.__init__(self, parent, id, title, position, size)

        self.Show()
        self.CreateStatusBar()
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.menubar.Append(self.fileMenu, '&File')

        self.Bind(wx.EVT_MENU, self.OnQuit,  self.fitem)

        self.SetMenuBar(self.menubar)
        self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.SetTitle('Owen and Ian in love in the USA')
        self.DrawingPanel = NodeTabPanel(self)
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

def main():

    ex = wx.App()
    WhereTheRibbonWillGo(None, wx.ID_ANY, "Le Drawing Panel", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()