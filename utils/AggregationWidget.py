import tkinter as tk
from tkinter import ttk
from typing import List


class AggregationWidget:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.frame: ttk.Frame = ttk.Frame(master=self.root)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.aggregation_methods: List[str] = [
            'R priority - default',
            'Weighted aggregation'
        ]

        
        self.chosen_method = tk.IntVar()
        for index, method in enumerate(self.aggregation_methods):
            ttk.Radiobutton(
                self.frame,
                text=method,
                variable=self.chosen_method,
                value=index
            ).pack()
        self.frame.pack(anchor=tk.N, fill=tk.BOTH)
            

    def get_method(self):
        try:
            self.aggregation_methods[self.chosen_method.get()]
        except:
            pass
