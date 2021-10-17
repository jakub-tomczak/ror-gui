import tkinter as tk
from tkinter import ttk
from typing import Dict
from ror.ResultAggregator import AbstractResultAggregator
from ror.ror_solver import AVAILABLE_AGGREGATORS


class AggregationWidget:
    def __init__(self, root: tk.Tk, method_from_parameters: str):
        self.root = root
        self.frame: ttk.Frame = ttk.Frame(master=self.root)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.__aggregation_methods: Dict[str, AbstractResultAggregator] = AVAILABLE_AGGREGATORS

        
        self.__chosen_method = tk.StringVar()
        for name in self.__aggregation_methods:
            radio_button = ttk.Radiobutton(
                self.frame,
                text=name,
                variable=self.__chosen_method,
                value=name
            )
            radio_button.pack()
        # pick currently selected method
        self.__chosen_method.set(method_from_parameters)
        self.frame.pack(anchor=tk.N, fill=tk.BOTH)
            

    def get_aggregation_method(self) -> AbstractResultAggregator:
        selected_method: str = self.__chosen_method.get()
        if selected_method is None or selected_method not in self.__aggregation_methods:
            valid_aggregation_methods = ", ".join(self.__aggregation_methods.keys())
            raise ValueError(f'Invalid aggregation method {selected_method} is selected. Valid aggregation methods are {valid_aggregation_methods}')
        return self.__chosen_method.get()
