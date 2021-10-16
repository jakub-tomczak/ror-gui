import tkinter as tk
from ror.Dataset import Dataset
from utils.Table import Table


class DataTab(tk.Frame):
    def __init__(self, root: tk.Tk):
        tk.Frame.__init__(self, root)
        self.table: Table = None
        self.init_gui()

    def init_gui(self):
        # data frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=9)
        self.grid(column=0, row=0, sticky=(tk.NSEW))
        self.__init_table()

    def __init_table(self):
        self.table = Table(self)
        self.table.grid(column=0, row=1, sticky=(tk.NSEW))

    def set_data(self, data: Dataset, display_precision: int = 2):
        if self.table is None:
            self.__init_table()
        self.table.set_data(data, display_precision)

    def clean_data(self):
        if self.table is not None:
            self.table.remove_data()
            self.table = None
