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

        if col == 4:
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
        self.dvc.AppendTextColumn("Title",  1, width=60, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("From",   2, width=47, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("To",   3, width=47,  mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Label",   4, width=44,  mode=dv.DATAVIEW_CELL_EDITABLE)
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
        b2 = wx.Button(self, label="Add Pipe",size=(65,23))
        self.Bind(wx.EVT_BUTTON, self.OnAddRow, b2)
        b3 = wx.Button(self, label="Del Pipe",size=(65,23))
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
                 'From Node %d' % id,
                 'To Node %d' % id,
                 'Label %d' % id]
        self.model.AddRow(value)
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(240,50), style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

#################################################################
'''PIPE INFO PANEL'''

class PipeInfoPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,140))

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

        text1 = wx.StaticText(panel, -1, "FROM")
        text2 = wx.StaticText(panel, -1, "TO")
        text3 = wx.StaticText(panel, -1, "COMMENT :")

        tctrl1 = wx.TextCtrl(panel, -1, "N34",size=(55,-1))
        tctrl2 = wx.TextCtrl(panel, -1, "N34567",size=(55,-1))
        tctrl3 = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)

        bmp1= wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp1, wx.BLUE)
        bmp1.SetMask(mask)

        button1 = wx.BitmapButton(self, -1, bmp1, (5, 5),
                       (bmp1.GetWidth(), bmp1.GetHeight()))
        button1.SetToolTipString("election From Map")

        bmp2= wx.Image("aquabutton.jpg",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp2, wx.BLUE)
        bmp2.SetMask(mask)

        button2 = wx.BitmapButton(self, -1, bmp2, (5, 5),
                       (bmp2.GetWidth(), bmp2.GetHeight()))
        button2.SetToolTipString("Selection From Map")


        # MAKE SIZERS
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)


        # ADD SIZERS APPROPRIATELY
        sizer1.Add(list_ctrl1, 0, wx.ALL|wx.EXPAND, 1)
        sizer1.Add(sizer2, 0, wx.ALL|wx.EXPAND, 1)
        sizer1.Add(sizer3, 0, wx.ALL|wx.EXPAND, 1)


        sizer3.Add(text3, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer3.Add(tctrl3, 2, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 1)

        sizer2.Add(text1, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer2.Add(tctrl1, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer2.Add(button1, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer2.Add(text2, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer2.Add(tctrl2, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer2.Add(button2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)


        panel.SetSizer(sizer1)
        panel.SetAutoLayout(1)
        sizer1.Fit(panel)

#################################################################
'''PHYSICAL PANEL'''

class PipePhysicalPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""

        wx.Panel.__init__(self, parent, -1,size=(240,130))
        panel = wx.Panel(self, -1)

        # sizers

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)

        # controls
        statictext1 = wx.StaticText(panel, -1, "Length")
        statictext2 = wx.StaticText(panel, -1, "Th.")


        bmp1 = wx.Image("aquabutton.jpg", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(bmp1, wx.BLUE)
        bmp1.SetMask(mask)
        bmpButton1 = wx.BitmapButton(self, -1, bmp1, (20, 20),
                       (bmp1.GetWidth(), bmp1.GetHeight()))
        bmpButton1.SetToolTipString("Selection From Map")

        textctrl1 = wx.TextCtrl(panel, -1, "2300", size=(40, -1))
        textctrl2 = wx.TextCtrl(panel, -1, "23", size=(40, -1))
        textctrl3 = wx.TextCtrl(panel, -1, "0.1", size=(40, -1))

        rButton1 = wx.RadioButton(panel, -1, "Stand.", size=(60, -1) )
        rButton2 = wx.RadioButton(panel, -1, "In Dia." , size=(60, -1))

        choices1 = [u"Km", u"Mile"]
        choices2 = [u"Choose", u"Choose Life", u"Choose a Jb", u"Choose a Career",  u"Choose a Family",
                    u"Choose FBT"]
        choices3 = [u"Meter", u"Feet"]

        choice1 = wx.Choice(panel, -1, choices=choices1, size=(60, -1))
        choice1.SetSelection(0)
        choice2 = wx.Choice(panel, -1, choices=choices2, size=(167, -1))
        choice2.SetSelection(0)
        choice3 = wx.Choice(panel, -1, choices=choices3, size=(60, -1))
        choice3.SetSelection(0)


        button1 = wx.Button(panel, 10, "Material Properties", (20, -1))

        # adding everything to their respective sizer

        sizer1.Add(sizer2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL ,1)
        sizer1.Add(sizer3, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 3)
        sizer1.Add(sizer4, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 3)
        sizer1.Add(sizer5, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 3)
        sizer1.Add(button1, 0,  wx.ALIGN_CENTRE | wx.ALL| wx.ALIGN_CENTER_VERTICAL, 3)

        sizer2.Add(statictext1, 1, wx.LEFT| wx.ALIGN_CENTER_VERTICAL , 3)
        sizer2.Add(textctrl1, 1, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)
        sizer2.Add(choice1, 1, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)
        sizer2.Add(bmpButton1, 1, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)

        sizer3.Add(rButton1, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 1)
        sizer3.Add(choice2, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 1)

        sizer4.Add(rButton2, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 1)
        sizer4.Add(textctrl2, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 1)
        sizer4.Add(statictext2, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL , 5)
        sizer4.Add(textctrl3, 0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 1)
        sizer4.Add(choice3, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL , 5)


        panel.SetSizer(sizer1)
        panel.SetAutoLayout(1)
        sizer1.Fit(panel)

#################################################################
'''PROPERTIES PANEL'''

class PipePropertiesPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, -1,size=(240,300))

        panel = wx.Panel(self, -1)

        ################# CONTROLS FIRST STATIC BOX
        box1 = wx.StaticBox(panel, -1, "METHOD SELECTION")
        box2 = wx.StaticBox(panel, -1, "CONDITIONS")

        sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
                      'six', 'seven', 'eight']

        combo = wx.ComboBox(panel, -1, "Choose Pipe Equation", (60,50),
                         (200, -1), sampleList,
                         wx.CB_DROPDOWN
                         #| wx.TE_PROCESS_ENTER
                         #| wx.CB_SORT
                         )

        statictext1 = wx.StaticText(panel, -1, "Pipe Eff.", size=(80, -1))
        statictext2 = wx.StaticText(panel, -1, "Roughness", size=(80, -1))
        statictext3 = wx.StaticText(panel, -1, "Friction F.", size=(80, -1))

        textctrl1 = wx.TextCtrl(panel, -1, "2300R", size=(60, -1))
        textctrl2 = wx.TextCtrl(panel, -1, "230F", size=(60, -1))

        spin = wx.SpinCtrlDouble(panel, value='0.00', pos=(75,50), size=(50,-1),
                                 min=-5.0, max=25.25, inc=0.25)
        spin.SetDigits(2)

        choices1 = [u"Unit", u"Books"]
        choices2 = [u"Celc.", u"Fahr."]

        choice1 = wx.Choice(panel, -1, choices=choices1, size=(60, -1))
        choice1.SetSelection(0)

        choice2 = wx.Choice(panel, -1, choices=choices1, size=(60, -1))
        choice2.SetSelection(0)

        ################# CONTROLS SECOND STATIC BOX #################
        rButton1 = wx.RadioButton(panel, -1, "Sim." )
        rButton2 = wx.RadioButton(panel, -1, "User" )

        t8 = wx.StaticText(panel, -1, "Base P.", size=(50, -1))
        t9 = wx.TextCtrl(panel, -1, "2300", size=(55, -1))
        t10 = wx.StaticText(panel, -1, "Base T.", size=(50, -1))
        t11 = wx.TextCtrl(panel, -1, "2300", size=(55, -1))

        choices3 = [u"KPa", u"PSI"]

        choice4 = wx.Choice(panel, -1, choices=choices3, size=(50, -1))
        choice4.SetSelection(0)

        choice5 = wx.Choice(panel, -1, choices=choices2, size=(50, -1))
        choice5.SetSelection(0)


################# CONTROLS THIRD STATIC BOX #################
        rButton3 = wx.RadioButton(panel, -1, "Sim." )
        rButton4 = wx.RadioButton(panel, -1, "User" )

        t12 = wx.StaticText(panel, -1, "Amb. P.", size=(50, -1))
        t13 = wx.TextCtrl(panel, -1, "2300", size=(55, -1))
        t14 = wx.StaticText(panel, -1, "Amb. T.", size=(50, -1))
        t15 = wx.TextCtrl(panel, -1, "2300", size=(55, -1))

        choice7 = wx.Choice(panel, -1, choices=choices3, size=(50, -1))
        choice7.SetSelection(0)

        choice8 = wx.Choice(panel, -1, choices=choices2, size=(50, -1))
        choice8.SetSelection(0)

        ################ SIZERS FIRST STATIC BOX ###############
        # SIZERS
        topsizer = wx.BoxSizer(wx.VERTICAL)
        staticSizer1 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        staticSizer2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)

        # ADD CONTROLS TO APPROPRIATE SIZERS
        topsizer.Add(staticSizer1, 0, wx.ALL, 3)
        topsizer.Add(staticSizer2, 0, wx.ALL, 3)

        staticSizer1.Add(combo, 0, wx.ALIGN_CENTRE | wx.ALL| wx.ALIGN_CENTER_VERTICAL| wx.FIXED_MINSIZE, 1)
        staticSizer1.Add(sizer3, 0, wx.ALL| wx.FIXED_MINSIZE, 2)
        staticSizer1.Add(sizer4, 0, wx.ALL| wx.FIXED_MINSIZE, 2)
        staticSizer1.Add(sizer5, 0, wx.ALL| wx.FIXED_MINSIZE, 2)

        sizer3.Add(statictext1, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 0)
        sizer3.Add(spin, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)

        sizer4.Add(statictext2,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 0)
        sizer4.Add(textctrl1, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        sizer4.Add(choice1, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL , 10)

        sizer5.Add(statictext3, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 0)
        sizer5.Add(textctrl2, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)
        sizer5.Add(choice2, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)

        ################ SIZERS SECOND STATIC BOX ###############


        sizer8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer12 = wx.BoxSizer(wx.HORIZONTAL)


        staticSizer2.Add(sizer8, 0, wx.ALL| wx.FIXED_MINSIZE, 3)
        staticSizer2.Add(sizer9, 0, wx.ALL| wx.FIXED_MINSIZE, 3)

        staticSizer2.Add(sizer11, 0, wx.ALL| wx.FIXED_MINSIZE, 3)
        staticSizer2.Add(sizer12, 0, wx.ALL| wx.FIXED_MINSIZE, 3)

        sizer8.Add(rButton1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer8.Add(t8,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL,5)
        sizer8.Add(t9,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 1)
        sizer8.Add(choice4,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)

        sizer9.Add(rButton2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer9.Add(t10, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)
        sizer9.Add(t11, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 1)
        sizer9.Add(choice5, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)


        sizer11.Add(rButton3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer11.Add(t12,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)
        sizer11.Add(t13,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 1)
        sizer11.Add(choice7,0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)

        sizer12.Add(rButton4, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer12.Add(t14, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 5)
        sizer12.Add(t15, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 1)
        sizer12.Add(choice8, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 10)
        #####################################

        panel.SetSizer(topsizer)
        topsizer.Fit(panel)
        panel.Move( (0,10) )

#################################################################
'''PIPE TAB SECTION'''

class PipeTabPanel(scrolled.ScrolledPanel):
     def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        self.SetBackgroundColour((202,223,244))

        pipedata = ListCtrl.pipedata.items()
        pipedata.sort()
        pipedata = [[str(k)] + list(v) for k,v in pipedata]

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(ListPanel(self, None, data=pipedata), 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 5)
        sizer.Add(PipeInfoPanel(self), 0, wx.TOP|wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 5)
        sizer.Add(PipePhysicalPanel(self), 0, wx.TOP| wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 0)
        sizer.Add(PipePropertiesPanel(self), 0, wx.TOP | wx.ALIGN_CENTRE_HORIZONTAL |wx.FIXED_MINSIZE, 0)



        self.SetSizerAndFit(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 1000

class WhereLeRibbonWillGo(wx.Frame):
    def __init__(self, parent, id, title, position, size):
        wx.Frame.__init__(self, parent, id, title, position, size)

        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.menubar.Append(self.fileMenu, '&File')

        self.Bind(wx.EVT_MENU, self.OnQuit,  self.fitem)

        self.SetMenuBar(self.menubar)
        self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.SetTitle('Owen and Ian in love in the USA')
        self.DrawingPanel = PipeTabPanel(self)
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

def main():

    ex = wx.App()
    WhereLeRibbonWillGo(None, wx.ID_ANY, "Le Drawing Panel", None, None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
