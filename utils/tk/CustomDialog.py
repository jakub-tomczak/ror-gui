from abc import abstractmethod
import tkinter as tk
from tkinter import ttk
from typing import Any

from tkinter import StringVar, simpledialog

class CustomDialog(tk.simpledialog.Dialog):
    def __init__(
        self,
        root: tk.Frame,
        header: str,
        submit_button_text: str = 'Submit',
        cancel_button_text: str = 'Cancel'
    ) -> None:
        self._on_cancel_text = StringVar(value=cancel_button_text)
        self._on_submit_text = StringVar(value=submit_button_text)
        self.__is_destroyed: bool = False
        super().__init__(root, header)

    @abstractmethod
    def _on_cancel(self):
        pass

    @abstractmethod
    def _on_submit(self, data):
        pass

    # function that takes root frame and builds GUI in it
    @abstractmethod
    def create_body(self, frame: tk.Frame):
        pass

    @abstractmethod
    def _validate(self) -> bool:
        pass

    def body(self, frame) -> tk.Frame:
        self.create_body(frame)
        return frame

    def ok_pressed(self):        
        if not self._validate():
            return
        data = self.get_data()
        self._on_submit(data)
        self._close()

    def cancel_pressed(self):
        if self._on_cancel is not None:
            self._on_cancel()
        self._close()

    def _close(self):
        if not self.__is_destroyed:
            self.destroy()
            self.__is_destroyed

    @abstractmethod
    def get_data(self) -> Any:
        '''
        This method should gather all data provided by user from dialog window
        and return it.
        '''
        pass

    def buttonbox(self):
        self.ok_button = ttk.Button(self, textvariable=self._on_submit_text, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = ttk.Button(self, textvariable=self._on_cancel_text, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())
