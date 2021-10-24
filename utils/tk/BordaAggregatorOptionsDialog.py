import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple
from utils.tk.AlphaValueCountSliderFrame import DEFAULT_NUMBER_OF_ALPHA_VALUES, AlphaValueCountSliderFrame
from utils.tk.CustomDialog import CustomDialog
from utils.AlphaValueWithWeight import AlphaValueWithWeight
import numpy as np


# number of alpha values, tie resolver
BordaAggregatorOptionsDialogResult = Tuple[int, List[AlphaValueWithWeight]]


class BordaAggregatorOptionsDialog(CustomDialog):
    def __init__(
        self,
        root: tk.Frame,
        header: str,
        on_submit_callback: Callable[[BordaAggregatorOptionsDialogResult], None],
    ) -> None:
        self.list_body: ttk.Frame = None
        self.__number_of_alpha_values: int = DEFAULT_NUMBER_OF_ALPHA_VALUES
        self.__on_submit = on_submit_callback
        super().__init__(root, header, submit_button_text='Solve', cancel_button_text='Cancel')

    def __change_alpha_value_number(self, number: int):
        self.__number_of_alpha_values = number

    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=2)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text='Set options for Borda aggregator', font=('Arial', 17), foreground='black')\
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

    def get_data(self) -> BordaAggregatorOptionsDialogResult:
        return (
            self.__number_of_alpha_values,
            [
                AlphaValueWithWeight(alpha, weight)
                for alpha, weight
                in zip(
                    np.linspace(start=0, stop=1, num=self.__number_of_alpha_values),
                    np.ones((self.__number_of_alpha_values)
                ))
            ]
        )
