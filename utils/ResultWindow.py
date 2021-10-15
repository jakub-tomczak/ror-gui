from math import floor
from os import close
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Widget
from typing import Callable, Dict, List
from ror.RORResult import RORResult
from ror.result_aggregator_utils import from_rank_to_alternatives
from ror.ror_solver import ProcessingCallbackData
from utils.ExplainAlternatives import ExplainAlternatives

from utils.ProgressBar import ProgressBar
from utils.ScrollableFrame import ScrollableFrame
from utils.Table import Table
from utils.image_helper import ImageDisplay
from utils.logging import Severity


class ResultWindow(tk.Frame):
    def __init__(
            self,
            logger: Callable[[str, Severity], None],
            window_object: tk.Tk,
            root: tk.Tk,
            close_callback: Callable[[tk.Frame], None] = None):
        tk.Frame.__init__(self, master=root)
        self.__logger: Callable[[str, Severity], None] = logger
        self.__window_object: tk.Tk = window_object
        self.__progress_bar: ProgressBar = None
        self.__results_data: Table = None
        self.__close_callback = close_callback
        self.top_frame: tk.Frame = None
        self.ranks_tab: ttk.Notebook = None
        self.final_image_frame: tk.Frame = None
        self.explain_alternatives_object: ExplainAlternatives = None
        self.init_gui()

    def init_gui(self):
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=7)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.__progress_bar = ProgressBar(self)
        self.__progress_bar.grid(row=0, column=0, columnspan=2, rowspan=3, sticky=tk.N, pady=50)
        tk.Button(self, text='Close solution', command=self.close_window)\
            .grid(column=0, columnspan=2, row=2)
        self.ranks_tab = ttk.Notebook(self)
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

    def __add_image(self, image: ImageDisplay):
        self.ranks_tab.add(image, text=f'{image.image_name}')

    def set_result(self, result: RORResult, alternatives: List[str]):
        # display all ranks
        if result is not None:
            # display intermediate ranks, associated with alpha values
            for rank in result.intermediate_ranks:
                alpha_value = rank.alpha_value
                image_path = rank.image_filename
                # create window with image
                image = ImageDisplay(
                    self.__logger,
                    self.__window_object,
                    self.ranks_tab,
                    image_path,
                    f'{alpha_value.name} rank'
                )
                self.__add_image(image)

            final_rank = result.final_rank
            final_image = ImageDisplay(
                self.__logger,
                self.__window_object,
                self.ranks_tab,
                final_rank.image_filename,
                'final rank'
            )
            self.__add_image(final_image)

            data_frame = tk.Frame(self)
            data_frame.grid(row=0, column=0, sticky=tk.NSEW)
            tk.Label(data_frame, text='Data - final result').pack(anchor=tk.N, fill=tk.BOTH, expand=1)

            # display ranks
            self.ranks_tab.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)

            self.__results_data = Table(data_frame)
            self.__results_data.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            self.__results_data.set_pandas_data(result.get_result_table())

            # explain result frame
            self.explain_alternatives_object = ExplainAlternatives(
                self,
                lambda alt_1, alt_2: f"{alt_1} vs {alt_2}: don't know why",
                alternatives
            )
            self.explain_alternatives_object.grid(row=1, column=0, sticky=tk.NSEW)

            # model frame
            # model_frame = tk.Frame(self.top_frame)
            # model_frame.grid(row=0, column=1, sticky=tk.NSEW)
            # tk.Label(model_frame, text='Model').pack(anchor=tk.NW, fill=tk.X)
            # constraints_root = ScrollableFrame(model_frame, 600)
            # constraints_root.pack(anchor=tk.W)
            # for constraint in result.model.constraints:
            #     tk.Label(constraints_root.frame, text=constraint, font=('Arial', 12)).pack(anchor=tk.W, fill=tk.X)


    def close_window(self):
        if self.__results_data is not None:
            self.__results_data.destroy()
            self.__results_data = None
        if self.__close_callback is not None:
            self.__close_callback(self.master)
        self.destroy()
