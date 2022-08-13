
import setting
import mod_function as func
import mod_style as sty
import mod_validate as vald

import math
import numbers
import numpy as np
import os
import pandas as pd
import time
import tkinter as tk
import tkinter.ttk as ttk


class Viewer(ttk.Treeview):
    """
    1. trigger data import function in the DataSource Class when Ctrl+V keypress is detected
    2. show the first x rows in preview window after import is completed
    """
    constWidth = 75                         # set a single column width in px
    constHeight = 10                        # set maximum number of rows for treeview

    def __init__(self, parent, DataSource):
        super(Viewer, self).__init__(parent)

        self.DataSource = DataSource
        self.Subset = pd.DataFrame()        # a portion of DataSource for preview
        self.SubsetColCount = 6             # default number of columns

        self.tree_style()
        self.tree_bind_events()
        self.tree_fill_rows()
        self.tree_column_width()

    def tree_bind_events(self):
        # add event listeners
        self.bind('<Control-v>', lambda x: self.event_on_paste())
        self.bind('<ButtonRelease>', lambda x: self.tree_column_width())
        self.bind("<FocusIn>", lambda x: self.configure(style='active.Treeview'))
        self.bind("<FocusOut>", lambda x: self.configure(style='inactive.Treeview'))
        # self.bind('<Button-3>', 'break')

    def event_on_paste(self, df=None):
        # import data from clipboard
        self.DataSource.reload(df=df)
        self.tree_refresh()

    def tree_refresh(self):
        # extract a portion of imported data
        self.Subset = self.DataSource.df.head(self.constHeight + 1).copy()      # +1 to include header row
        self.Subset = self.Subset.fillna('.')
        self.SubsetColNames = self.Subset.iloc[0]                               # get header
        self.Subset = self.Subset.iloc[1:]                                      # keep only data rows

        self.tree_clear()
        self.tree_fill_heading()
        self.tree_fill_rows()
        self.tree_column_width()

    def tree_clear(self):
        # delete all rows
        for iid in self.get_children():
            self.delete(iid)
        # reset column id and column heading
        self.SubsetColCount = max(6, len(self.SubsetColNames))
        self['column'] = list(range(self.SubsetColCount))
        for i in range(self.SubsetColCount):
            self.heading(i, text='')

    def tree_fill_heading(self):
        # update column heading
        for i in range(len(self.SubsetColNames)):
            self.heading(i, text=self.SubsetColNames[i])

    def tree_fill_rows(self):
        # read rows from Subset
        for r in self.Subset.itertuples(index=False):
            self.insert('', tk.END, values=r, tags=(r[0],))
        # fill up all unused row spaces if total rows < constHeight
        # side note: treeview must contain at least 1 empty row to trigger FocusIn event
        while len(self.get_children()) < self.constHeight:
            self.insert('', tk.END, values='')

    def tree_column_width(self):
        # maintain constant column width even user manually adjusted the width
        for c in range(self.SubsetColCount):
            self.column(c, stretch='NO', width=self.constWidth)

    def tree_style(self):
        # config tabular view
        self['column'] = list(range(6))
        self['height'] = self.constHeight
        self['show'] = 'headings'
        self['selectmode'] = 'none'
        # apply ttk style (refer to mod_style.py)
        self.style = sty.TTKStyle()
        self['style'] = 'inactive.Treeview'
        self.style.map('Treeview',
                       foreground=sty.fixed_treeview_map(self, 'foreground'),
                       background=sty.fixed_treeview_map(self, 'background'))


class ScrollableContainer(tk.Frame):
    """
    this Frame Class is a container with scrollbar
    """
    def __init__(self, parent, width, height, borderwidth, scroll):
        super(ScrollableContainer, self).__init__(parent)

        self.width = width
        self.height = height

        self.configure(borderwidth=borderwidth, relief='groove')
        self.canvas = tk.Canvas(self, highlightthickness=0)

        if scroll == 1:
            self.scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollbar.pack(side="bottom", fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar.set)
            self.canvas.pack(side='top')
        elif scroll == 2:
            self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.pack(side='left')
        else:
            self.canvas.pack(side='left')

        self.innerFrame = tk.Frame(self.canvas)
        self.innerFrame.pack()

        self.canvas.create_window((0, 0), window=self.innerFrame, anchor='nw')
        self.innerFrame.bind("<Configure>", self.maintain_width)

    def maintain_width(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=self.width, height=self.height)


class LogWindow(ttk.Treeview):
    """
    this widget serves the purpose of displaying message at various stage of operation
    1. insert new message into the Message Window
    2. latest message or important message is always highlighted
    3. only a fixed number of message are kept, old messages are discarded
    """
    constWidth = 450                # set a single column width in px
    constHeight = 12                # set maximum number of rows for treeview

    def __init__(self):
        super(LogWindow, self).__init__()

        self.tree_style()
        self.tree_bind_events()

    def tree_style(self):
        # config the tabular view style
        self['column'] = list(range(1))
        self['height'] = self.constHeight
        self['show'] = 'headings'
        # set initial width
        self.tree_column_width(list(range(1)))
        self.heading(0, text='Message Window', anchor='w')
        # apply ttk style (refer to mod_style.py)
        self.style = sty.TTKStyle()
        self['style'] = 'LogWindow.Treeview'
        self.style.map('Treeview',
                       foreground=sty.fixed_treeview_map(self, 'foreground'),
                       background=sty.fixed_treeview_map(self, 'background'))

        # highlight message with different color according to 'tag' attribute
        self.tag_configure('latest', background='#ebfff0', foreground='#228B22', font=('Arial', 9))
        self.tag_configure('important', background='#ffe5e5', foreground='red', font=('Arial', 9))

    def tree_bind_events(self):
        self.bind('<ButtonRelease>', lambda x: self.tree_column_width(list(range(1))))

    def add(self, text, tag=''):
        # clean up existing items first
        self.tree_item_cleanup()

        # insert new items
        tag = 'latest' if (tag != 'important') else tag
        self.insert('', tk.END, values=[text], tags=(tag,))

        # always scroll to the bottom
        bottom = self.get_children()[-1]
        self.focus(bottom)
        self.see(bottom)
        # self.selection_set(bottom)

    def tree_item_cleanup(self):
        currentHeight = len(self.get_children())
        i = 0
        for iid in self.get_children():
            # tagging of non-important message are wiped out as opposite to important message,
            # as a result all important messages are always highlighted
            if 'important' not in self.item(iid, "tags"):
                self.item(iid, tags='')
            # delete item if max. row is reached
            if currentHeight - self.constHeight >= i:
                self.delete(iid)
            i += 1

    # maintain constant column width even user manually adjusted the width
    def tree_column_width(self, columns):
        for c in columns:
            self.column(c, stretch='NO', width=self.constWidth)


class PopUp(tk.Toplevel):
    """
    the built-in tkinter messagebox makes an alarming sound when it appears, this widget is a silent replacement
    """
    def __init__(self, parent, title, message):
        tk.Toplevel.__init__(self, parent)
        # call modal form
        self.root = parent
        self.transient(parent)
        self.grab_set()

        # set attribute of modal form
        self.geometry('+{0}+{1}'.format(parent.winfo_rootx() + 300, parent.winfo_rooty() + 250))
        self.title(title)
        self.resizable(0, 0)

        # arrange visual components
        self.icon = sty.Drawing(self)
        self.icon.draw_previewer_icon('completed')
        self.icon.grid(row=0, column=0, padx=(20, 0))
        ttk.Label(self, text=message, wraplength=250, anchor='center').grid(row=0, column=1, padx=20, pady=20)
        ttk.Button(self, text='OK', command=self.destroy).grid(row=1, column=1, padx=20, pady=20)


class ModalForm(tk.Toplevel):
    """
    1. this class prompt a modal form to gather user options on an operation
    2. user interface are built dynamically according to values passed from argument "option"
    3. user options are gathered and they are passed to parent form through argument "option"
    :return null
    """
    def __init__(self, parent, command, DataSourceA, DataSourceB, option, pic, param):
        tk.Toplevel.__init__(self, parent)
        # call modal form
        self.root = parent
        self.transient(parent)
        self.grab_set()

        # set modal form attribute
        self.left_x = parent.winfo_rootx()
        self.top_y = parent.winfo_rooty()
        self.geometry_adjust()
        self.title('Options - ' + setting.alias[command])
        self.resizable(0, 0)

        # initialize objects and variables
        self.command = command
        self.option = option                            # updatable
        self.DataSourceA = DataSourceA
        self.DataSourceB = DataSourceB
        self.colListA = []
        self.colListB = []
        self.user_controls = []                         # a list to hold user controls created for each user option
        self.param = param                              # updatable

        # populate the modal form interface
        ttk.Label(self, image=pic.get('example_' + command), borderwidth=2, relief="ridge").grid(row=0, columnspan=2, sticky='w', padx=10, pady=10)
        self.read_col_name()
        self.create_user_controls()
        ttk.Button(self, text='Run', command=self.close_form).place(relx=0.5, rely=0.95, anchor='center')

    def geometry_adjust(self, addW=0, addH=0, addX=0, addY=0):
        self.geometry('{0}x{1}+{2}+{3}'.format(550 + addW, 550 + addH, self.left_x + 300 + addX, self.top_y + addY))

    def read_col_name(self):
        self.colListA = ([''] + self.DataSourceA.df.iloc[0, :].tolist()) if len(self.DataSourceA.df) > 0 else []
        self.colListB = ([''] + self.DataSourceB.df.iloc[0, :].tolist()) if len(self.DataSourceB.df) > 0 else []

    def create_user_controls(self):
        # append dataset id (0 = Dataset A, 1 = Dataset B) into list if dataset is non-empty
        loadedDataset = [idx for idx in range(2) if len([self.colListA, self.colListB][idx]) > 0]
        # create a list to trace frames that should not be created more than once
        framesCreated = []

        # create user control for each user option
        i = 1
        for option, value in self.option.items():
            if option in ['optJoinColumns', 'optDeltaColumns', 'optAggNum', 'optAggText']:
                # the variable itemList determines selectable items in combobox
                if option in ['optJoinColumns']:
                    itemList = {
                        1: self.colListA,
                        2: self.colListB
                    }
                elif option in ['optDeltaColumns']:
                    itemList = {
                        1: self.colListA
                    }
                elif option in ['optAggNum', 'optAggText']:
                    itemList = {
                        1: self.colListA if len(self.colListA) > 0 else self.colListB
                    }
                # set layout of the combobox
                args = {
                    'optJoinColumns':   {'width': 270, 'scroll': 0, 'layout': 'parallel', 'addH':  90},
                    'optDeltaColumns':  {'width': 135, 'scroll': 2, 'layout': 'parallel', 'addH': 150},
                    'optAggNum':        {'width': 135, 'scroll': 0, 'layout': 'overlay',  'addH': 180},
                    'optAggText':       {'width': 135, 'scroll': 0, 'layout': 'overlay',  'addH': 180}
                }
                # create frame
                frame = ttk.LabelFrame(self, text=setting.optDesc[option])
                frame.grid(row=i, column=0, sticky='w', padx=10, pady=6)
                # create container for combobox
                container = ScrollableContainer(frame, args[option]['width'], 160, 0, scroll=args[option]['scroll'])
                container.pack(expand=True, fill='x')
                # create combobox
                holder = []
                for col in itemList.keys():
                    for j in range(len(value)):
                        if args[option]['layout'] == 'parallel':
                            pos = col                                   # place side by side
                        elif args[option]['layout'] == 'overlay':
                            pos = 1                                     # place by overlay
                        var = tk.StringVar()
                        var.set('')                                     # default value
                        obj = ttk.Combobox(container.innerFrame, textvariable=var, values=itemList[col], state='readonly', width=15)
                        obj.var = var                                   # bind "var" to any object to prevent unset by garbage collection
                        obj.grid(row=j, column=pos, sticky='w', padx=10, pady=5)
                        holder.append(obj)                              # put all created combobox into a list
                obj = holder
                self.geometry_adjust(addH=args[option]['addH'])         # extend window height to accommodate all boxes
            elif option in ['optSeparator']:
                # create frame
                frame = ttk.Frame(self)
                frame.grid(row=i, column=0, columnspan=2, sticky='w', padx=10, pady=6)
                # create label
                label = ttk.Label(frame, text=setting.optDesc[option])
                label.grid(row=0, column=0, sticky='w')
                # create combo box
                var = tk.StringVar()
                var.set(',')
                obj = ttk.Combobox(frame, textvariable=var, values=setting.sepList, state='readonly', width=3)
                obj.var = var
                obj.grid(row=0, column=1, sticky='w', padx=(10, 0))
            elif option in ['optJoinMode', 'optDataSet']:
                # create frame
                frame = ttk.LabelFrame(self, text='Others')
                frame.grid(row=i, column=0, columnspan=2, sticky='w', padx=10, pady=6)
                # create radio buttons
                var = tk.IntVar()
                var.set(value)
                n = 0
                for desc in setting.optDesc[option].split('|'):
                    if option == 'optJoinMode':
                        obj = ttk.Radiobutton(frame, text=desc.strip(), value=n, variable=var)
                    elif option == 'optDataSet':
                        frame.config(text='Target Dataset')
                        obj = ttk.Radiobutton(frame, text=desc.strip(), value=n, variable=var, command=lambda: self.switch_dataset())
                        obj.configure(state='normal' if (n in loadedDataset) else 'disabled')
                    n += 1
                    obj.var = var
                    obj.grid(row=i+n, column=0, sticky='w', padx=10, pady=6)
                # select a loaded dataset by default
                if option == 'optDataSet':
                    var.set(loadedDataset[0])
            else:
                # create frame (only once)
                if option in ['optIgnoreCase', 'optTrim', 'optTrimZero']:
                    if self.command in ['run_join']:
                        caption = 'Join key treatment'
                    else:
                        caption = 'Text treatment'
                    frameCaption = caption
                    frameName = 'frame_key'
                else:
                    frameCaption = 'Other options'
                    frameName = 'frame_others'
                if frameName not in framesCreated:
                    framesCreated.append(frameName)
                    frame = ttk.LabelFrame(self, text=frameCaption)
                    frame.grid(row=i, column=0, columnspan=2, sticky='w', padx=10, pady=6)
                # create checkbox
                var = tk.IntVar()
                var.set(value)                        # default value (either 0 or 1)
                obj = ttk.Checkbutton(frame, text=setting.optDesc[option], variable=var, onvalue=1, offvalue=0)
                obj.var = var
                obj.grid(row=i, column=0, sticky='w', padx=10, pady=6, columnspan=2)
            i += 1
            # put all created user controls into variable "user_control"
            self.user_controls.append(obj)
            # select dataset that is not empty
            self.switch_dataset()

    def switch_dataset(self):
        side_idx = 0
        # check whether Dataset A or B was chosen
        for option, obj in zip(self.option.keys(), self.user_controls):
            if option in ['optDataSet']:
                side_idx = obj.var.get()
        # refresh items in combo box with chosen dataset
        for option, obj in zip(self.option.keys(), self.user_controls):
            if option in ['optAggNum', 'optAggText']:
                for combo in obj:
                    combo.configure(values=[self.colListA, self.colListB][side_idx])
                    combo.current(0)

    def close_form(self):
        newOption = dict()
        # retrieve values selected by user from each user control
        for key, obj in zip(self.option.keys(), self.user_controls):
            if key in ['optJoinColumns', 'optDeltaColumns', 'optAggNum', 'optAggText']:
                # retrieve a list if user control is a collection of combobox
                if isinstance(obj, list):
                    value = [combo.current() for combo in obj]
            else:
                value = obj.var.get()
            newOption[key] = value

        # validate user inputs
        warnings = vald.validate_user_option(self.command, newOption, self.DataSourceA, self.DataSourceB)
        if len(warnings) > 0:
            # ... fail -> display popup warning, user stays on the modal form
            raise Exception(warnings[0], 'w')
        else:
            # ... succeed -> proceed
            for key, value in newOption.items():
                if isinstance(value, list):
                    # minus 1 on all combo box index since the first item is a dummy item
                    newOption[key] = [v-1 for v in value if (v != 0)]
            # pass a variable indicating that ok button had been pressed
            self.param['commit'] = 1
            # return user inputs through dictionary update method
            self.option.update(newOption)
            self.destroy()


class SettingForm(tk.Toplevel):
    """
    1. prompt a modal form to accept setting changes
    2. return user decisions to parent form through argument "option"
    """
    def __init__(self, parent, pic, param):
        tk.Toplevel.__init__(self, parent)
        # call modal form
        self.root = parent
        self.transient(parent)
        self.grab_set()

        # set modal form attribute
        self.left_x = parent.winfo_rootx()
        self.top_y = parent.winfo_rooty()
        self.geometry('{0}x{1}+{2}+{3}'.format(450, 250, self.left_x+250, self.top_y+150))
        self.title('Settings')
        self.resizable(0, 0)

        # initialize objects and variables
        self.param = param
        self.user_controls = dict()

        # create label
        ttk.Label(self, text='Adjust the maximum row and maximum and column allowed.').grid(
            row=0, column=0, columnspan=2, sticky='w', padx=10
        )

        # create frame
        frame = ttk.Frame(self)
        frame.grid(
            row=1, column=0
        )

        # set spinbox attribute
        s = setting.limits
        lim1 = {'key': 'maxRow', 'desc': 'Maximum number of rows',
                 'current': s['maxRow'], 'lowBound': s['maxRowInit'], 'upBound': s['maxRowInit'] * 2, 'step': 10000}
        lim2 = {'key': 'maxCol', 'desc': 'Maximum number of columns',
                 'current': s['maxCol'], 'lowBound': s['maxColInit'], 'upBound': s['maxColInit'] * 4, 'step': 10}
        lim3 = {'key': 'maxKeyCol', 'desc': 'Maximum number of key columns',
                 'current': s['maxKeyCol'], 'lowBound': s['maxKeyColInit'], 'upBound': s['maxKeyColInit'] + 10, 'step': 1}
        lim4 = {'key': 'maxNumCol', 'desc': 'Maximum number of numeric columns',
                 'current': s['maxNumCol'], 'lowBound': s['maxNumColInit'], 'upBound': s['maxNumColInit'] + 10, 'step': 1}
        limits = [lim1, lim2, lim3, lim4]

        # create spinbox
        for i, lim in enumerate(limits):
            var = tk.IntVar()
            var.set(lim['current'])                  # default value
            ttk.Label(frame, text=lim['desc']).grid(row=i*2, column=0, sticky='w', padx=10)
            obj = ttk.Spinbox(frame, textvariable=var, from_=lim['lowBound'], to=lim['upBound'], increment=lim['step'], state='readonly', width=10, justify='right')
            obj.var = var
            obj.grid(row=i*2, column=1, sticky='e', padx=10, pady=10)

            self.user_controls[lim['key']] = obj

        # create OK button
        ttk.Button(self, text='Confirm', command=self.close_form).place(relx=0.50, rely=0.85, anchor='center')

    def close_form(self):
        self.param['commit'] = 1
        for key, obj in self.user_controls.items():
            self.param['limit'].update({key: obj.var.get()})
        self.destroy()


class MemoryUsage(ttk.Label):
    """
    this is a label that shows total memory consumed by DataSource widgets
    """
    def __init__(self):
        super(MemoryUsage, self).__init__()
        self.memUsed = dict()
        self.style = sty.TTKStyle()
        self['style'] = 'MemoryUsage.Label'

        self.refresh()

    def refresh(self, name=None, df=None):
        if name is not None and df is not None and len(df) > 0:
            self.memUsed.update({name: df.memory_usage(deep=True).sum()})
        totalUsed = sum(self.memUsed.values())
        self.configure(text='Total Dataset Size: ' + str(round(totalUsed / 1048576, 1)) + 'MB')
