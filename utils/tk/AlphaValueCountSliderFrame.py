from tkinter import IntVar, ttk
import tkinter as tk
from typing import Callable

DEFAULT_NUMBER_OF_ALPHA_VALUES = 3
MAX_NUMBER_OF_ALPHA_VALUES = 15


class AlphaValueCountSliderFrame(ttk.Frame):
    def __init__(
        self,
        master: ttk.Frame,
        on_value_changed: Callable[[int], None],
        initial_value: int
    ) -> None:
        super().__init__(master=master)
        self.__on_value_changed: Callable[[int], None] = on_value_changed
        self.__number_of_alpha_values: IntVar = IntVar(value=initial_value)
        self.__init_gui()

    def __slider_value_changed(self, value: str):
        try:
            val = float(value)
            val = round(val)
            self.__number_of_alpha_values.set(val)
            if self.__on_value_changed is not None:
                self.__on_value_changed(val)
        except:
            pass

    def __init_gui(self):
        inner_fr = ttk.Frame(self, padding=20)
        inner_fr.columnconfigure(0, weight=1)
        inner_fr.columnconfigure(1, weight=19)
        inner_fr.rowconfigure(0, weight=1)
        inner_fr.rowconfigure(1, weight=1)
        ttk.Label(inner_fr, text='Number of alpha values').grid(
            row=0, column=0, sticky=tk.W)
        ttk.Label(inner_fr, textvariable=self.__number_of_alpha_values).grid(
            row=0, column=1, sticky=tk.W)
        ttk.Scale(
            inner_fr,
            from_=DEFAULT_NUMBER_OF_ALPHA_VALUES,
            to=MAX_NUMBER_OF_ALPHA_VALUES,
            orient='horizontal',
            command=self.__slider_value_changed
        ).grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        inner_fr.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
