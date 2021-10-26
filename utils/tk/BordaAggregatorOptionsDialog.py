import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple
from utils.tk.AlphaValueCountSliderFrame import DEFAULT_NUMBER_OF_ALPHA_VALUES, AlphaValueCountSliderFrame
from utils.tk.CustomDialog import CustomDialog
import numpy as np


# number of alpha values, voting method name {Borda or Copeland}
BordaCopelandAggregatorOptionsDialogResult = Tuple[int, str]


class BordaCopelandAggregatorOptionsDialog(CustomDialog):
    def __init__(
        self,
        root: tk.Frame,
        header: str,
        voting_method_name: str,
        on_submit_callback: Callable[[BordaCopelandAggregatorOptionsDialogResult], None],
    ) -> None:
        self.list_body: ttk.Frame = None
        self.__number_of_alpha_values: int = DEFAULT_NUMBER_OF_ALPHA_VALUES
        self.__on_submit = on_submit_callback
        self.voting_method_name = voting_method_name
        super().__init__(root, header, submit_button_text='Solve', cancel_button_text='Cancel')

    def __change_alpha_value_number(self, number: int):
        self.__number_of_alpha_values = number

    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=2)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text=f'Set options for {self.voting_method_name} aggregator', font=('Arial', 17), foreground='black')\
            .grid(row=0, column=0, sticky=tk.EW)
        AlphaValueCountSliderFrame(self.list_body, self.__change_alpha_value_number, self.__number_of_alpha_values)\
            .grid(row=1, column=0, sticky=tk.NSEW)
        return self.list_body

    def _on_submit(self, data):
        if self.__on_submit is not None:
            self._close()
            self.__on_submit(data)

    def _on_cancel(self):
        pass

    def _validate(self) -> bool:
        return True

    def get_data(self) -> BordaCopelandAggregatorOptionsDialogResult:
        return (
            self.__number_of_alpha_values,
            self.voting_method_name
        )
