from abc import abstractmethod
import tkinter as tk
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
        self.destroy()

    def cancel_pressed(self):
        if self._on_cancel is not None:
            self._on_cancel()
        self.destroy()

    @abstractmethod
    def get_data(self) -> Any:
        '''
        This method should gather all data provided by user from dialog window
        and return it.
        '''
        pass

    def buttonbox(self):
        self.ok_button = tk.Button(self, textvariable=self._on_submit_text, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(self, textvariable=self._on_cancel_text, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())

# class CustomDialog(tk.Toplevel):
#     def __init__(self,
#         root: tk.Tk,
#         header_name: str = None,
#         on_cancel: Callable[[None], None] = None,
#         on_cancel_text: str = 'Cancel',
#         on_submit: Callable[[None], Any] = None,
#         on_submit_text: str = 'Submit'
#     ) -> None:
#         super().__init__(master=root)
#         self.__header_name: tk.StringVar = tk.StringVar()
#         self.set_header_name(header_name) 
#         self.__on_cancel = on_cancel
#         self.__on_cancel_text = on_cancel_text
#         self.__on_submit = on_submit
#         self._on_submit_text = on_submit_text

#         self.__init_gui()

#         self.__min_width = 400
#         self.__min_height = 400
#         self.minsize(self.__min_width, self.__min_height)
#         self.geometry(f'{self.__min_width}x{self.__min_height}')
#         self.title(self.__header_name.get())
#         self.grid()
        
#     def __init_gui(self):
#         # for header
#         self.rowconfigure(0, weight=1)
#         # for content
#         self.rowconfigure(1, weight=9)
#         # for bottom buttons
#         self.rowconfigure(2, weight=1)
#         self.columnconfigure(0, weight=1)

#         # header
#         tk.Label(self, textvariable=self.__header_name).grid(row=0, column=0, sticky=tk.NSEW)

#         # data
#         # to be set by set_data method. root for data's frame should be taken using data_root_object property

#         # bottom buttons
#         buttons_frame = tk.Frame(self)
#         buttons_frame.grid(row=2, column=0, sticky=tk.N)
#         submit_button = tk.Button(
#             buttons_frame,
#             text=self._on_submit_text,
#             command=lambda: self.__on_submit_self()
#         )
#         submit_button.pack(anchor=tk.CENTER, side=tk.LEFT, fill=tk.Y, expand=0)

#         cancel_button = tk.Button(
#             buttons_frame,
#             text=self.__on_cancel_text,
#             command=lambda: self.__on_cancel_self()
#         )
#         cancel_button.pack(anchor=tk.CENTER, side=tk.RIGHT, fill=tk.Y, expand=0)

#     @property
#     def data_root_object(self) -> tk.Frame:
#         return self

#     def set_header_name(self, name: str):
#         self.__header_name.set(name)

#     def set_data(self, data: tk.Frame):
#         data.grid(row=1, column=0, sticky=tk.NSEW)

#     @abstractmethod
#     def get_data(self) -> Any:
#         '''
#         This method should gather all data provided by user from dialog window
#         and return it.
#         '''
#         pass

#     def __on_submit_self(self):
#         if self.__on_submit is not None:
#             data = self.get_data()
#             self.__on_submit(data)
#         self.destroy()

#     def __on_cancel_self(self):
#         if self.__on_cancel is not None:
#             self.__on_cancel()
#         self.destroy()

        