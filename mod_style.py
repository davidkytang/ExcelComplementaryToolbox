
import contextlib
import tkinter
import tkinter as tk
import tkinter.ttk as ttk

import mod_function as func
import setting


# ------------------------------------------------------ #
# Reusable Styles
# ------------------------------------------------------ #
class TTKStyle(ttk.Style):

    def __init__(self):
        super(TTKStyle, self).__init__()
        # treeview
        self.configure('active.Treeview',
                       foreground='#343434', background='#fff9ef', fieldbackground='#fff9ef', font=('Arial', 9))
        self.configure('active.Treeview.Heading',
                       foreground='#343434', font=('Tahoma', 8, 'bold'))
        self.configure('inactive.Treeview',
                       foreground='#313131', background='#fafafa ', fieldbackground='#f9f9f9', font=('Arial', 9))
        self.configure('inactive.Treeview.Heading',
                       foreground='#9a9a9a', font=('Tahoma', 8, 'bold'))

        self.configure('LogWindow.Treeview',
                       foreground='#68B0AB', font=('Arial', 9))
        self.configure('LogWindow.Treeview.Heading',
                       foreground='#343434', font=('Arial', 9, 'bold'))
        # label
        self.configure('MemoryUsage.Label',
                       foreground='slategray4', font=('Arial', 8))


# ------------------------------------------------------ #
# Image Gallery
# ------------------------------------------------------ #
class Gallery:

    def __init__(self):
        self.basePath = setting.img_path
        self.pictures = dict()
        self.alerted = False

    def get(self, filename):
        try:
            # prevent existing image in the dictionary from being overwritten, otherwise those image will be reloaded
            # and objects shared the image will lose the reference
            if filename not in self.pictures:
                self.pictures[filename] = tk.PhotoImage(file=self.basePath + filename + '.png')
            return self.pictures[filename]

        except tkinter.TclError:
            # display popup warning message if a image file is not found
            if self.alerted is False:
                # ensure the message only appears once
                self.alerted = True
                # if missing file is detected before app.mainloop() is executed, which means
                # report_callback_exception_new is not yet available, call custom function alert() to display exception
                e = Exception('Image library is incomplete ('
                              + filename + '.png is missing). Please re-download the image folder again.'
                              + '\n\nPress OK to continue.', 'w')
                func.alert(e)


# ------------------------------------------------------ #
# Canvas generated visual components
# ------------------------------------------------------ #
class Drawing(tk.Canvas):

    def __init__(self, parent):
        super(Drawing, self).__init__(parent)
        self.pic = Gallery()
        self.img = tk.PhotoImage()

    def draw_previewer_caption(self, text, side):
        self.img = self.pic.get('icon_' + side)
        self['width'] = 200
        self['height'] = 30
        self.create_image(18, 18, image=self.img)
        self.create_text(30, 18, text=text, fill='green', font=('Arial Black', 11, ''), anchor='w')

    def draw_previewer_icon(self, name):
        if name == 'completed':
            self['width'] = 64
            self['height'] = 64
            self.img = self.pic.get('icon_complete')
            self.create_image(2, 2, image=self.img, anchor='nw')

    def draw_loading_screen(self):
        self.img = self.pic.get('loading')
        self['width'] = 337
        self['height'] = 60
        # self['bg'] = 'white'
        self['bd'] = 0
        self['highlightthickness'] = 0
        self.create_image(0, 0, image=self.img, anchor='nw')

    def draw_separator(self):
        self['width'] = 1000
        self['height'] = 3
        self.create_rectangle(0, 0, 1000, 3, outline='white', fill='gray')

    def draw_profiling_caption(self, text):
        self['width'] = 710
        self['height'] = 30
        self['bg'] = 'white'
        self['bd'] = 0
        self['highlightthickness'] = 0
        self.create_text(0, 10, text=text, fill='skyblue4', font=('Arial Black', 11, ''), anchor='w')
        self.create_rectangle(0, 29, 710, 30, width=0, fill='azure3')


# ------------------------------------------------------ #
# Miscellaneous
# ------------------------------------------------------ #
def fixed_treeview_map(treeview, option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    return [elm for elm in treeview.style.map('Treeview', query_opt=option)
            if elm[:2] != ('!disabled', '!selected')]

