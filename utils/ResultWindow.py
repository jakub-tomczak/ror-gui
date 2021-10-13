from math import floor
from os import close
import tkinter as tk
from tkinter.ttk import Widget
from typing import Callable, Dict
from ror.RORResult import RORResult
from ror.result_aggregator_utils import from_rank_to_alternatives
from ror.ror_solver import ProcessingCallbackData

from utils.ProgressBar import ProgressBar
from utils.ScrollableFrame import ScrollableFrame
from utils.Table import Table
from utils.image_helper import ImageDisplay
from utils.logging import Severity


class ResultWindow(tk.Frame):
    def __init__(self, logger: Callable[[str, Severity], None], window_object: tk.Tk, root: tk.Tk, close_callback: Callable[[tk.Frame], None] = None):
        tk.Frame.__init__(self, master=root)
        self.__logger: Callable[[str, Severity], None] = logger
        self.__window_object: tk.Tk = window_object
        self.image_windows: Dict[str, ImageDisplay] = dict()
        self.__progress_bar: ProgressBar = None
        self.__results_data: Table = None
        self.__close_callback = close_callback
        self.top_frame: tk.Frame = None
        self.__scrollable_area_intermediate_ranks: ScrollableFrame = None
        self.__scrollable_area_final_rank: ScrollableFrame = None

        self.init_gui()

    def init_gui(self):
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=7)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=9)
        self.__progress_bar = ProgressBar(self)
        self.__progress_bar.grid(row=0, column=0, columnspan=2, rowspan=3, sticky=tk.N, pady=50)
        tk.Button(self, text='Close solution', command=self.close_window)\
            .grid(column=0, columnspan=2, row=2)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.update()

    def __set_progress(self, value: int, status: str):
        self.__progress_bar.report_progress(value, status)
        
        if self.__progress_bar is not None and value == 100:
            self.__progress_bar.destroy()
            self.__progress_bar = None

    def report_progress(self, data: ProcessingCallbackData):
        self.__set_progress(floor(data.progress*100), data.status)
        self.update()

    def set_result(self, result: RORResult):
        # display all ranks
        if result is not None:
            self.__scrollable_area_intermediate_ranks = ScrollableFrame(self, ImageDisplay.IMAGE_WIDTH*3)
            self.__scrollable_area_intermediate_ranks.grid(row=1, column=1, sticky=tk.NSEW)
            self.__scrollable_area_final_rank = ScrollableFrame(self, ImageDisplay.IMAGE_WIDTH*3)
            self.__scrollable_area_final_rank.grid(row=1, column=0, sticky=tk.NSEW)
            # display intermediate ranks, associated with alpha values
            for rank in result.intermediate_ranks:
                alpha_value = rank.alpha_value
                image_path = rank.image_filename
                if alpha_value.name in self.image_windows and self.image_windows[alpha_value.name] is not None:
                    # reuse window if still open
                    self.image_windows[alpha_value.name].change_image(image_path)
                else:
                    # create window with image
                    self.image_windows[alpha_value.name] = ImageDisplay(
                        self.__logger,
                        self.__window_object,
                        self.__scrollable_area_intermediate_ranks.frame,
                        image_path,
                        f'{alpha_value.name} rank'
                    )
                    self.image_windows[alpha_value.name].pack(anchor=tk.CENTER, fill=tk.X, expand=True)

            final_rank = result.final_rank
            if 'final_rank' in self.image_windows:
                self.image_windows['final_rank'].change_image(final_rank.image_filename)
            else:
                self.image_windows['final_rank'] = ImageDisplay(
                    self.__logger,
                    self.__window_object,
                    self.__scrollable_area_final_rank.frame,
                    final_rank.image_filename,
                    'final rank'
                )
                self.image_windows['final_rank'].pack(anchor=tk.CENTER, fill=tk.X, expand=True)

            self.top_frame = tk.Frame(self)
            self.top_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
            self.top_frame.rowconfigure(0, weight=1)
            self.top_frame.columnconfigure(0, weight=1)
            self.top_frame.columnconfigure(1, weight=1)
            data_frame = tk.Frame(self.top_frame)
            data_frame.grid(row=0, column=0, sticky=tk.NSEW)
            tk.Label(data_frame, text='Data - final result').pack(anchor=tk.NW, fill=tk.X, expand=1)

            self.__results_data = Table(data_frame)
            self.__results_data.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            self.__results_data.set_pandas_data(result.get_result_table())

            model_frame = tk.Frame(self.top_frame)
            model_frame.grid(row=0, column=1, sticky=tk.NSEW)
            tk.Label(model_frame, text='Model').pack(anchor=tk.NW, fill=tk.X)
            constraints_root = ScrollableFrame(model_frame, 600, True)
            constraints_root.pack(anchor=tk.W)
            for constraint in result.model.constraints:
                tk.Label(constraints_root.frame, text=constraint, font=('Arial', 12)).pack(anchor=tk.W, fill=tk.X)


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
