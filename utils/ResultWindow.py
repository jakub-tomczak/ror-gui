from math import floor
from os import close
import tkinter as tk
from typing import Callable, Dict
from ror.RORResult import RORResult
from ror.ror_solver import ProcessingCallbackData

from utils.ProgressBar import ProgressBar
from utils.Table import Table
from utils.image_helper import ImageDisplay


class ResultWindow(tk.Frame):
    def __init__(self, root: tk.Tk, close_callback: Callable[[tk.Frame], None] = None):
        tk.Frame.__init__(self, master=root)
        self.image_windows: Dict[str, ImageDisplay] = dict()
        self.__progress_bar: ProgressBar = None
        self.__results_data: Table = None
        self.__close_callback = close_callback

        self.init_gui()

    def init_gui(self):
        self.rowconfigure(0, weight=10)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.__progress_bar = ProgressBar(self)
        self.__progress_bar.grid(row=0, column=0, columnspan=2, rowspan=2)
        tk.Button(self, text='Close solution', command=self.close_window)\
            .grid(column=0, columnspan=2, row=1)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.update()

    def __set_progress(self, value: int, status: str):
        self.__progress_bar.report_progress(value, status)
        if value == 100:
            self.__progress_bar.destroy()

    def report_progress(self, data: ProcessingCallbackData):
        self.__set_progress(floor(data.progress*100), data.status)
        self.update()

    def set_result(self, result: RORResult):
        # display all ranks
        if result is not None:
            # display intermediate ranks, associated with alpha values
            for rank in result.intermediate_ranks:
                alpha_value = rank.alpha_value
                image_path = rank.image_filename
                if alpha_value.name in self.image_windows and self.image_windows[alpha_value.name] is not None:
                    # reuse window if still open
                    self.image_windows[alpha_value.name].change_image(image_path)
                else:
                    # create window with image
                    self.image_windows[alpha_value.name] = ImageDisplay(self, image_path, f'{alpha_value.name} rank')

            final_rank = result.final_rank
            if 'final_rank' in self.image_windows:
                self.image_windows['final_rank'].change_image(final_rank.image_filename)
            else:
                self.image_windows['final_rank'] = ImageDisplay(self, final_rank.image_filename, 'final rank')

        self.__results_data = Table(self)
        self.__results_data.grid(row=0, column=0, sticky=tk.NW)
        self.__results_data.set_pandas_data(result.get_result_table())

    def close_window(self):
        if self.image_windows is not None:
            for image_display in self.image_windows.values():
                image_display.destroy()
            self.image_windows = None
        if self.__results_data is not None:
            self.__results_data.destroy()
            self.__results_data = None
        if self.__close_callback is not None:
            self.__close_callback(self.master)
        self.destroy()
