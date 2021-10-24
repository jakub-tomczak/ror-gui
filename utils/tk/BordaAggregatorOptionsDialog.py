import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple
from utils.tk.AlphaValueCountSliderFrame import DEFAULT_NUMBER_OF_ALPHA_VALUES, AlphaValueCountSliderFrame
from utils.tk.CustomDialog import CustomDialog
from ror.ror_solver import TIE_RESOLVERS

from utils.tk.TieResolverPicker import TieResolverPicker


# number of alpha values, tie resolver
BordaAggregatorOptionsDialogResult = Tuple[int, str]


class BordaAggregatorOptionsDialog(CustomDialog):
    def __init__(
        self,
        root: tk.Frame,
        header: str,
        on_submit_callback: Callable[[BordaAggregatorOptionsDialogResult], None],
    ) -> None:
        self.list_body: ttk.Frame = None
        self.__number_of_alpha_values: int = DEFAULT_NUMBER_OF_ALPHA_VALUES
        self.__resolver: TieResolverPicker = None
        self.__on_submit = on_submit_callback
        super().__init__(root, header, submit_button_text='Solve', cancel_button_text='Cancel')

    def __change_alpha_value_number(self, number: int):
        self.__number_of_alpha_values = number

    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=2)
        self.list_body.rowconfigure(2, weight=6)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text='Set options for Borda aggregator', font=('Arial', 17), foreground='black')\
            .grid(row=0, column=0, sticky=tk.EW)
        AlphaValueCountSliderFrame(self.list_body, self.__change_alpha_value_number, self.__number_of_alpha_values)\
            .grid(row=1, column=0, sticky=tk.NSEW)
        self.__resolver = TieResolverPicker(self.list_body, TIE_RESOLVERS, 'NoResolver')\
            .grid(row=2, column=0, sticky=tk.NSEW)
        return self.list_body

    def _on_submit(self, data):
        if self.__on_submit is not None:
            self.__on_submit(data)

    def _on_cancel(self):
        pass

    def _validate(self) -> bool:
        return True

    def get_data(self) -> BordaAggregatorOptionsDialogResult:
        return (
            self.__number_of_alpha_values,
            self.__resolver.tie_resolver_name
        )
