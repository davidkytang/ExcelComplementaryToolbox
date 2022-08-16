
import setting
import mod_data as data
import mod_gui as gui
import mod_function as func
import mod_style as sty
import mod_validate as vald
import operation as operation

import contextlib
import numpy as np
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk


class MainApp(tk.Tk):

    def __init__(self):
        super(MainApp, self).__init__()

        # switch between debug mode
        debugMode = False

        # create Image Library
        self.Pic = sty.Gallery()

        # set attributes for the main form
        self.title('Excel Complementary Toolbox')
        self.iconphoto(False, self.Pic.get('icon'))
        self.geometry(func.centered_window(self, 970, 630))
        self.resizable(0, 0)

        # supersede default exception handler of tkinter
        if not debugMode:
            self.report_callback_exception = self.report_callback_exception_new

        # create Message Window
        self.Log = gui.LogWindow()
        self.Log.add('Data should contain a header row and at least 2 columns.')
        self.Log.add('Copy data from Excel and click one of above frames to paste (Ctrl + V).')

        # create Memory Consumption Reader
        self.Mem = gui.MemoryUsage()

        # create Log for Conversion Error
        self.ErrorTracker = data.ConversionErrorTracker()

        # create User Options for retrieving user inputs
        self.Option = data.Parameters()

        # create Data Source
        self.DataSourceA = data.DataSource(self, name='a', limit=setting.limits, mem=self.Mem, log=self.Log)
        self.DataSourceB = data.DataSource(self, name='b', limit=setting.limits, mem=self.Mem, log=self.Log)

        # create Data Previewer
        self.ContainerA = gui.ScrollableContainer(self, 450, 222, 1, scroll=1)
        self.ContainerB = gui.ScrollableContainer(self, 450, 222, 1, scroll=1)
        self.TreeA = gui.Viewer(self.ContainerA.innerFrame, self.DataSourceA)
        self.TreeB = gui.Viewer(self.ContainerB.innerFrame, self.DataSourceB)

        # create Data Work (interim dataset created after transformation of original data source)
        self.DataWorkA = data.DataWork()
        self.DataWorkB = data.DataWork()

        # arrange position of visual objects
        self.ContainerA.grid(row=1,column=0, sticky='nsew', padx=(20, 0), pady=(0, 10))
        self.ContainerB.grid(row=1,column=2, sticky='nsew', padx=(20, 0), pady=(0, 10))
        self.TreeA.pack(expand=True, fill='both')
        self.TreeB.pack(expand=True, fill='both')
        self.Log.grid(row=3, column=0, sticky='nsew', padx=(20, 0), pady=(0, 20))
        self.Mem.grid(row=4, column=2, sticky='se', padx=(0, 0), pady=(8, 0))

        # create dataset swap button
        ttk.Button(self, text='Swap', image=self.Pic.get('button_swap'), compound='left',
                   command=lambda: self.swap_data_source()
                   ).grid(row=2, column=2, sticky='e')

        # create a button group for all operations
        self.container = tk.LabelFrame(self, text=' Operations ',
                                       font=('Arial', 10, 'bold'))  # borderwidth=0, highlightthickness=0
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=3, column=2, pady=(0, 40))

        ttk.Button(self.container, text=setting.alias['run_profiling'], image=self.Pic.get('run_profiling'), compound='top', command=lambda: self.generate_result('run_profiling')).grid(
            row=0, column=0, padx=20, pady=10)
        ttk.Button(self.container, text=setting.alias['run_join'], image=self.Pic.get('run_join'), compound='top', command=lambda: self.generate_result('run_join')).grid(
            row=0, column=1, padx=20, pady=10)
        ttk.Button(self.container, text=setting.alias['run_aggregation'], image=self.Pic.get('run_aggregation'), compound='top', command=lambda: self.generate_result('run_aggregation')).grid(
            row=0, column=2, padx=20, pady=10)

        ttk.Button(self.container, text=setting.alias['run_compare_value'], image=self.Pic.get('run_compare_value'), compound='top', command=lambda: self.generate_result('run_compare_value')).grid(
            row=1, column=0, padx=20, pady=10)
        ttk.Button(self.container, text=setting.alias['run_exception'], image=self.Pic.get('run_exception'), compound='top', command=lambda: self.generate_result('run_exception')).grid(
            row=1, column=1, padx=20, pady=10)
        ttk.Button(self.container, text=setting.alias['run_connection'], image=self.Pic.get('run_connection'), compound='top', command=lambda: self.generate_result('run_connection')).grid(
            row=1, column=2, padx=20, pady=10)

        # create setting button
        ttk.Button(self, text='Settings', image=self.Pic.get('data_sheet'), compound='left', command=lambda: self.show_setting()).grid(
            row=3, column=2, pady=10, sticky='es')

        # draw other decorative graphics
        self.canvas_top_caption_A = sty.Drawing(self)
        self.canvas_top_caption_A.draw_previewer_caption('Dataset A (preview)', 'a')
        self.canvas_top_caption_A.grid(row=0, column=0, sticky='wn', padx=(10, 0))

        self.canvas_top_caption_B = sty.Drawing(self)
        self.canvas_top_caption_B.draw_previewer_caption('Dataset B (preview)', 'b')
        self.canvas_top_caption_B.grid(row=0, column=2, sticky='wn', padx=(10, 0))

        self.canvas_line = sty.Drawing(self)
        self.canvas_line.draw_separator()
        self.canvas_line.grid(row=4, column=0, columnspan=99, sticky='nw')

        # create a button group for debug functions
        if debugMode:
            ttk.Label(self, text="Debug Mode", background="red", foreground="white").grid(row=4, column=0, sticky='sw', pady=(0,0))
            frame = ttk.LabelFrame()
            frame.grid(row=3, column=2, sticky='s')

            ttk.Button(frame, command=lambda: self.load_test_data(), text='Load Test Data').grid(row=0, column=1)
            ttk.Button(frame, command=lambda: self.dump_data(self), text='dump').grid(row=0, column=2)

    def transform_data(self, DataSource, DataWork, command):
        DataWork.copy_df(df=DataSource.df)
        DataWork.set_column_roles(self.Option, command)
        DataWork.generate_interim_fields(self.Option, self.ErrorTracker, self.Log)

    def generate_result(self, command):
        # display popup warning when basic requirement is not fulfilled
        vald.validate_source(command, self.DataSourceA, self.DataSourceB)

        # get corresponding user options
        self.Option.set(setting.operationParam[command])

        # create a flag to capture whether OK button has been pressed
        param = {'commit': 0}

        # prompt modal form
        modal = gui.ModalForm(self, command, self.DataSourceA, self.DataSourceB, self.Option, self.Pic, param)

        # freeze the main window until modal form is dismissed
        self.wait_window(modal)

        # exit current subroutine if user did not press OK button
        if param['commit'] == 0:
            return

        self.waiting_message('show')

        # transform the datasets
        sel = self.Option.get('optDataSet')
        if (sel == 0) or (sel is None):
            self.transform_data(self.DataSourceA, self.DataWorkA, command)
        if (sel == 1) or (sel is None):
            self.transform_data(self.DataSourceB, self.DataWorkB, command)

        # collect statistic on errors from numeric conversion function
        failSample = self.ErrorTracker.collect_sample()
        if len(failSample) > 0:
            self.Log.add('Below character values cannot be converted to number and will be treated as 0:', tag='important')
            for colName, sample in failSample.items():
                colName = colName if len(colName) < 20 else colName[:20] + '...'
                self.Log.add('➜【{0}】 ‟{1}” '.format(colName, '”, ‟'.join(sample)), tag='important')

        # run operation
        count, complete = operation.run_operation(self, command,
                                                  self.DataSourceA, self.DataSourceB, self.DataWorkA, self.DataWorkB,
                                                  self.Option)

        self.waiting_message('hide')

        # show record count
        if count >= 0:
            self.Log.add(setting.alias[command] + ' - Complete ({0:,} rows of result copied to clipboard).'.format(count))
        # display popup message upon completion
        if complete >= 0:
            modal = gui.PopUp(self, 'Completed',
                              'Result is ready.\n\nYou could press [Ctrl + V] on a blank Excel sheet to get the result.'
                              )
            self.wait_window(modal)

    def report_callback_exception_new(self, exc, val, tb):
        """
        pop up a warning message interrupting the execution without terminating the program.
        """
        func.alert(val)
        # mute error if somehow <waiting_message> function does not exist
        with contextlib.suppress(AttributeError):
            self.waiting_message('hide')

    def swap_data_source(self):
        # raise warning if one of dataset is empty
        if (len(self.DataSourceA.df.columns) == 0 or len(self.DataSourceB.df.columns) == 0):
            raise Exception('Unable to swap because one of the dataset is empty.')
        # swap underlying dataframe
        temp = self.DataSourceA.df
        self.DataSourceA.df = self.DataSourceB.df
        self.DataSourceB.df = temp
        # swap columns names
        self.DataSourceA.df.columns = self.DataSourceA.df.columns.map(lambda c: str(c).replace('b', 'a'))
        self.DataSourceB.df.columns = self.DataSourceB.df.columns.map(lambda c: str(c).replace('a', 'b'))
        # refresh Data Previewer
        self.TreeA.tree_refresh()
        self.TreeB.tree_refresh()

    def waiting_message(self, action):
        """
        display a message on the main window when data is being processed.
        """
        if action == 'show':
            self.LabelLoading = sty.Drawing(self)
            self.LabelLoading.draw_loading_screen()
            self.LabelLoading.place(relx=0.5, rely=0.46, anchor='center')
            self.update_idletasks()
        elif action == 'hide':
            self.LabelLoading.destroy()

    def show_setting(self):
        """
        pop up a modal form for the adjustment of default settings
        """
        param = {
            'commit': 0,              # to capture whether OK button has been pressed
            'limit': {}               # a collection of new setting values
        }

        # prompt modal form
        modal = gui.SettingForm(self, self.Pic, param)

        # deactivate the main window until modal form is dismissed
        self.wait_window(modal)

        # update to new settings
        if param['commit'] == 1:
            setting.limits.update(param['limit'])

    """ ---------------------- start debugging assistant ------------------------------ """
    def load_test_data(self):
        df1 = pd.read_csv('res/ds_test_a.csv', encoding='utf-8')
        df2 = pd.read_csv('res/ds_test_b.csv', encoding='utf-8')
        self.TreeA.event_on_paste(df=df1)
        self.TreeB.event_on_paste(df=df2)

    def dump_data(self, top):
        win = tk.Toplevel(top)
        win.geometry('+800+80')
        t = ttk.Label(win, text="", background="white")
        t.pack()
        txt = ''
        txt += self.DataSourceA.df.head(5).to_string() + '\n\n' + self.DataWorkA.df.head(5).to_string() + '\n\n'
        txt += self.DataSourceB.df.head(4).to_string() + '\n\n' + self.DataWorkB.df.head(4).to_string() + '\n\n'
        txt += str(self.Option)
        t.configure(text=txt)
    """ ---------------------- end debugging assistant ------------------------------ """


if __name__ == '__main__':

    app = MainApp()
    app.mainloop()

