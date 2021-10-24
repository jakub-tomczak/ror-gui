import tkinter as tk
from tkinter import ttk
from typing import Callable
from utils.tk.CustomDialog import CustomDialog
from utils.tk.TieResolverPicker import TieResolverPicker
import numpy as np
from ror.ror_solver import TIE_RESOLVERS

# number of alpha values, tie resolver
DefaultAggregatorOptionsDialogResult = str


class DefaultAggregatorOptionsDialog(CustomDialog):
    def __init__(
        self,
        root: tk.Frame,
        header: str,
        on_submit_callback: Callable[[DefaultAggregatorOptionsDialogResult], None],
    ) -> None:
        self.list_body: ttk.Frame = None
        self.__tie_resolver: TieResolverPicker = None
        self.__on_submit = on_submit_callback
        super().__init__(root, header, submit_button_text='Solve', cancel_button_text='Cancel')

    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=2)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text='Set options for Default aggregator', font=('Arial', 17), foreground='black')\
            .grid(row=0, column=0, sticky=tk.EW)
        self.__tie_resolver = TieResolverPicker(self.list_body, TIE_RESOLVERS, 'NoResolver')
        self.__tie_resolver.grid(row=1, column=0, sticky=tk.NSEW)
        return self.list_body

    def _on_submit(self, data):
        if self.__on_submit is not None:
            self._close()
            self.__on_submit(data)

    def _on_cancel(self):
        pass

    def _validate(self) -> bool:
        return True

    def get_data(self) -> DefaultAggregatorOptionsDialogResult:
        return self.__tie_resolver.tie_resolver_name
