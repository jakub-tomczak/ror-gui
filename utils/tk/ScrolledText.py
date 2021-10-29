import tkinter as tk
from tkinter import ttk
from tkinter.constants import RIGHT, LEFT, Y, X, BOTH

from utils.time import get_log_time

WARNING = 'warning'
ERROR = 'error'
INFO = 'info'

START_LINE = 1


class ScrolledText(tk.Text):
    '''
    ScrolledText implementation copied from the original ScrolledText.
    Added textvariable to handle binded text.
    '''

    def __init__(self, window_object: tk.Tk, master=None, **kw):
        self.frame: ttk.Frame = ttk.Frame(master)
        self.vbar: ttk.Scrollbar = ttk.Scrollbar(self.frame)
        self.button_frame: ttk.Frame = ttk.Frame(self.frame)
        self.button_frame.pack(side=RIGHT, fill=Y)
        self.__window_object: tk.Tk = window_object
        self.clear_button: ttk.Button = ttk.Button(text="Clear log", master=self.button_frame, command=lambda: self.clear())
        self.clear_button.pack(anchor=tk.N, fill=X)
        self.copy_button: ttk.Button = ttk.Button(text='Copy log', master=self.button_frame, command=lambda: self.__copy_all())
        self.copy_button.pack(anchor=tk.S, fill=X)
        self.vbar.pack(side=RIGHT, fill=BOTH)

        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview
        self.__line = START_LINE

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(
            tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __copy_all(self):
        # get field value from event, but remove line copy text label and return at end
        text = self.get_text()
        self.__window_object.clipboard_clear()  # clear clipboard contents
        self.__window_object.clipboard_append(text)  # append new value to clipbaord
        self.add_text(f'[{get_log_time()}][LOGGER] Copied log content to clipboard!', 'SlateGray4')

    def clear(self):
        self.configure(state='normal')
        self.delete(1.0, tk.END)
        # remove all tags to clear formatting in further logs
        all_tags = self.tag_names()
        for tag in all_tags:
            self.tag_delete(tag)
        # reset line
        self.__line = START_LINE
        self.configure(state='disabled')

    def get_text(self):
        text = self.get(1.0, tk.END)
        if text is not None and text != '':
            return text.strip()
        return ''

    def set_text(self, value, color=None):
        self.clear()
        self.add_text(value, color)

    def add_text(self, value, color=None):
        line_to_index = lambda line: f'{line}.0'
        if value is not None:
            self.configure(state='normal')
            _data = f'{value.strip()}\n'
            self.insert(line_to_index(self.__line), _data)
            if color is not None:
                tag_name = f'line_{self.__line}'
                self.tag_add(tag_name, line_to_index(self.__line), line_to_index(self.__line+1))
                self.tag_configure(tag_name, foreground=color)
            self.__line += 1
            self.configure(state='disabled')
            # scroll to the end
            self.see('end')

    def __str__(self):
        return str(self.frame)
