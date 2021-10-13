import tkinter as tk
from tkinter import ttk
from tkinter.constants import RIGHT, LEFT, Y, X, BOTH

WARNING = 'warning'
ERROR = 'error'
INFO = 'info'


class ScrolledText(tk.Text):
    '''
    ScrolledText implementation copied from the original ScrolledText.
    Added textvariable to handle binded text.
    '''

    def __init__(self, master=None, textvariable=None, **kw):
        self.frame: ttk.Frame = ttk.Frame(master)
        self.vbar: ttk.Scrollbar = ttk.Scrollbar(self.frame)
        self.button_frame: ttk.Frame = ttk.Frame(self.frame)
        self.button_frame.pack(side=RIGHT, fill=Y)
        self.clear_button: ttk.Button = ttk.Button(text="Clear", master=self.button_frame)
        self.clear_button.pack(anchor=tk.S, fill=X)
        self.save_button: ttk.Button = ttk.Button(text="Save", master=self.button_frame, command=lambda: self.set_text("asdsad"))
        self.save_button.pack(anchor=tk.N, fill=X)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        if textvariable is not None:
            if not isinstance(textvariable, tk.Variable):
                raise TypeError(
                    "tkinter.Variable type expected, {} given.".format(type(textvariable)))
            self.textvariable = textvariable
            self.textvariable.get = self.get_text
            self.textvariable.set = self.set_text

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(
            tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def clear(self):
        self.delete(1.0, tk.END)

    def get_text(self):
        text = self.get(1.0, tk.END)
        if text is not None and text != '':
            return text.strip()
        return None

    def set_text(self, value):
        print("setting text", value)
        self.clear()
        if value is not None:
            self.insert(tk.END, value.strip())

    def __str__(self):
        return str(self.frame)
