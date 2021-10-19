from os import remove
from tkinter import ttk
import tkinter as tk
from typing import Callable, List
from utils.AlphaValue import AlphaValue
import ror.alpha as ror_alpha

from utils.AlphaValueWidget import AlphaValueWidget
from utils.ScrollableFrame import ScrollableFrame
from utils.Severity import Severity


class AlphaValuesFrame:
    def __init__(self, root: tk.Tk, logger: Callable[[str, Severity], None]):
        self.root = tk.Frame(root)

        self.root.rowconfigure(0, weight=9)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.scrollable_content: ScrollableFrame = ScrollableFrame(self.root, 170)
        self.scrollable_content.grid(row=0, column=0, sticky=tk.NSEW)

        self.__alpha_values: List[AlphaValue] = []
        self.logger = logger

        ttk.Button(
                master=self.root,
                text='Add alpha value',
                command=self.__add_alpha_value
        ).grid(row=1, column=0, sticky=tk.NSEW)

        self.add_alpha_value('Q', 0.0)
        self.add_alpha_value('R', 0.5)
        self.add_alpha_value('S', 1.0)


    def add_alpha_value(self, name: str, value: float) -> AlphaValueWidget:
        if not AlphaValueWidget.validate_name(name, self.logger) or not AlphaValueWidget.validate_value(value, self.logger):
            self.logger('Failed to add new alpha value')
            return None
        new_alpha_value = self.__add_alpha_value()
        new_alpha_value.alpha_value.name.set(name)
        new_alpha_value.alpha_value.value.set(value)

    def __add_alpha_value(self) -> AlphaValueWidget:
        widget = AlphaValueWidget(self.scrollable_content.frame, self.logger, self.__update_on_removal)
        widget.pack(anchor=tk.NW, fill=tk.X, expand=1)
        self.__alpha_values.append(widget.alpha_value)
        self.scrollable_content.force_scroll_update()
        return widget

    def __update_on_removal(self, removed_alpha_value: AlphaValue):
        self.logger(f'Removing rank {removed_alpha_value.name.get()} with alpha value {removed_alpha_value.value.get()}')
        try:
            self.__alpha_values.remove(removed_alpha_value)
        except:
            self.logger(f'Element {removed_alpha_value} was not found')
        self.scrollable_content.force_scroll_update()

    def get_all_alpha_values(self) -> List[ror_alpha.AlphaValue]:
        return [alpha.to_ror_alpha_value() for alpha in self.__alpha_values]