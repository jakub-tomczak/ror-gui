from tkinter import ttk
import tkinter as tk
from typing import Any, Callable

from utils.AlphaValue import AlphaValue
from utils.Severity import Severity


class AlphaValueWidget(ttk.Frame):
    def validate_name(new_name: str, logger: Callable[[str, Severity], None]):
        if len(new_name) > 15:
            logger(
                'rank name\'s length must be lower than 15 characters', Severity.ERROR)
            return False
        return True

    def validate_value(new_value: float, logger: Callable[[str, Severity], None]):
        try:
            if new_value == '':
                return True
            val = float(new_value)
            if not 0.0 <= val <= 1.0:
                logger('value must be in range <0.0, 1.0>', Severity.ERROR)
                return False
            return True
        except:
            logger('value must be float value', Severity.ERROR)
            return False

    def __init__(self, root: ttk.Frame, logger: Callable[[str, Severity], None], on_destroy_callback: Callable[[AlphaValue], None] = None):
        ttk.Frame.__init__(self, master=root)
        self.alpha_value: AlphaValue = AlphaValue()
        self.logger = logger
        self.remove_button: ttk.Button() = None
        self.rowconfigure(0, weight=9)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        # -- register validation callback --
        name_validator_callback = root.register(AlphaValueWidget.validate_name)
        value_validator_callback = root.register(
            AlphaValueWidget.validate_value)
        # -- name --
        ttk.Label(self, text='Rank name').pack(anchor=tk.N, fill=tk.X)
        name_entry = ttk.Entry(self, textvariable=self.alpha_value.name)
        name_entry.config(validate='key', validatecommand=(
            name_validator_callback, '%P'))
        name_entry.pack(anchor=tk.N, fill=tk.X)
        # -- value --
        ttk.Label(self, text='Alpha value').pack(anchor=tk.N, fill=tk.X)
        value_entry = ttk.Entry(self, textvariable=self.alpha_value.value)
        value_entry.config(validate='key', validatecommand=(
            value_validator_callback, '%P'))
        value_entry.pack(anchor=tk.N, fill=tk.X)
        # -- remove button --
        self.__destroy_callback: Callable[[Any], None] = on_destroy_callback
        ttk.Button(master=self, text='Remove', command=self.__destroy).pack(
            anchor=tk.N, fill=tk.X)

    def __destroy(self):
        if self.__destroy_callback is not None:
            # pass None event
            self.__destroy_callback(self.alpha_value)
        self.destroy()
