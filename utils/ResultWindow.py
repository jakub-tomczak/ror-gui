from math import floor
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple
from pandas.core import accessor
from ror.RORParameters import RORParameters
from ror.RORResult import RORResult
from ror.Relation import Relation
from ror.loader_utils import RORParameter
from ror.ror_solver import ProcessingCallbackData
from utils.ExplainAlternatives import ExplainAlternatives
from utils.PreferenceRelationsFrame import PreferenceRelationsFrame
from ror.WeightedResultAggregator import WeightedResultAggregator
from utils.PreferenceIntensityRelationsFrame import PreferenceIntensityRelationsFrame

from utils.ProgressBar import ProgressBar
from utils.ScrollableFrame import ScrollableFrame
from utils.Table import Table
from utils.image_helper import ImageDisplay
from utils.Severity import Severity
from utils.tk.io_helper import save_model
from utils.type_aliases import LoggerFunc


class ResultWindow(tk.Frame):
    def __init__(
            self,
            logger: Callable[[str, Severity], None],
            window_object: tk.Tk,
            root: tk.Tk,
            close_callback: Callable[[tk.Frame], None] = None):
        tk.Frame.__init__(self, master=root)
        self.__logger: LoggerFunc = logger
        self.__window_object: tk.Tk = window_object
        self.__progress_bar: ProgressBar = None
        self.__results_data: Table = None
        self.__solution_properties_tab: tk.Frame = None
        self.__close_callback = close_callback
        self.top_frame: tk.Frame = None
        self.ranks_tab: ttk.Notebook = None
        self.final_image_frame: tk.Frame = None
        self.__overview: ttk.Notebook = None
        self.__ror_result: RORResult = None
        self.__ror_parameters: RORParameters = None
        self.explain_alternatives_object: ExplainAlternatives = None
        self.init_gui()

    def init_gui(self):
        self.rowconfigure(0, weight=9)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.__progress_bar = ProgressBar(self)
        self.__progress_bar.grid(row=0, column=0, columnspan=2, rowspan=3, sticky=tk.N, pady=50)
        ttk.Button(self, text='Close solution', command=self.close_window)\
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
        self.ranks_tab.add(image, text=f'{image.image_name}', compound=tk.TOP, sticky=tk.NSEW, underline=2)

    def set_result(self, result: RORResult, alternatives: List[str], parameters: RORParameters):
        # display all ranks
        if result is not None:
            self.__ror_result = result
            self.__ror_parameters = parameters
            # display ranks
            # notebook tabs exchanges
            # however scrollbar in each tab behaves as one scrollbar - 
            # if you use scrollbar on 2nd tab and then go to the 3rd
            # then focus is not changed to tab3
            self.ranks_tab.grid(row=0, column=1, sticky=tk.NSEW)
            # def tab_changed(event):
            #     print('tab has changed', event)
            # self.ranks_tab.bind("<<NotebookTabChanged>>", tab_changed)
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
                image.pack(fill=tk.BOTH, expand=1)
                self.__add_image(image)

            final_rank = result.final_rank
            final_image = ImageDisplay(
                self.__logger,
                self.__window_object,
                self.ranks_tab,
                final_rank.image_filename,
                'final rank'
            )
            final_image.pack(fill=tk.BOTH, expand=1)
            self.__add_image(final_image)

            self.ranks_tab.select(0)
            details_frame = ttk.Frame(self)
            details_frame.grid(row=0, column=0, sticky=tk.NSEW)

            # overview notebook
            self.__overview = ttk.Notebook(details_frame)
            self.__overview.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)

            data_tab = ttk.Frame(self.__overview)
            data_tab.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            self.__overview.add(data_tab, text='Data')

            self.__results_data = Table(data_tab)
            ttk.Label(data_tab, text='Data - final result')\
                .pack(anchor=tk.NW)
            self.__results_data.set_pandas_data(
                result.get_result_table(),
                display_precision=parameters.get_parameter(RORParameter.PRECISION)
            )
            self.__results_data.pack(anchor=tk.N, fill=tk.BOTH, expand=1)

            self.__solution_properties_tab = ttk.Frame(self.__overview)
            self.__overview.add(self.__solution_properties_tab, text='Model properties')

            self.__solution_properties_tab.rowconfigure(0, weight=1)
            self.__solution_properties_tab.rowconfigure(1, weight=1)
            self.__solution_properties_tab.rowconfigure(2, weight=1)
            
            # parameters
            parameters_frame = tk.Frame(self.__solution_properties_tab)
            parameters_frame.grid(row=0, sticky=tk.NSEW)
            # parameters_frame.pack(anchor=tk.NW, expand=1, fill=tk.X)

            ttk.Label(parameters_frame, text='Parameters', font=('Arial', 17)).pack(anchor=tk.NW)
            method_parameters: List[Tuple[str, str]] = []
            for parameter in RORParameter:
                if type(result.results_aggregator) is not WeightedResultAggregator and parameter == RORParameter.ALPHA_WEIGHTS:
                    # don't add weights parameter if not using WeightedResultAggregator
                    continue
                method_parameters.append((parameter.value, result.parameters.get_parameter(parameter)))
            parameters_table = Table(parameters_frame)
            parameters_table.set_simple_data(method_parameters)
            parameters_table.pack(anchor=tk.NW, fill=tk.X, expand=0)

            # add preference relations
            preferences_frame = tk.Frame(self.__solution_properties_tab)
            preferences_frame.grid(row=1, sticky=tk.NSEW)
            ttk.Label(preferences_frame, text='Preference relations', font=('Arial', 17)).pack(anchor=tk.NW) #.grid(row=0, sticky=tk.NW)
            preferences_windows = ttk.Frame(preferences_frame)
            preferences_windows.rowconfigure(0, weight=1)
            preferences_windows.columnconfigure(0, weight=1)
            preferences_windows.columnconfigure(1, weight=1)
            preferences_windows.pack(anchor=tk.NW, fill=tk.X, expand=1)
            preferences = PreferenceRelationsFrame(preferences_windows, result.model.dataset, False, self.__logger)
            preferences.grid(row=0, column=0, sticky=tk.NSEW)
            intensity_preferences = PreferenceIntensityRelationsFrame(preferences_windows, result.model.dataset, False, self.__logger)
            intensity_preferences.grid(row=0, column=1, sticky=tk.NSEW)

            buttons = ttk.Frame(self.__solution_properties_tab)
            # buttons.pack(anchor=tk.NW)
            buttons.grid(row=2, sticky=tk.EW)
            buttons.rowconfigure(0, weight=1)
            for col in range(4):
                buttons.columnconfigure(col, weight=1)
            ttk.Button(
                buttons,
                text='Save model',
                command=lambda: self.__save_model()
            ).grid(row=0, column=1, sticky=tk.NSEW)
            ttk.Button(
                buttons,
                text='Save model to latex',
                command=lambda: self.__save_model()
            ).grid(row=0, column=2, sticky=tk.NSEW)

            # explain result frame
            self.explain_alternatives_object = ExplainAlternatives(
                self,
                result.results_aggregator.explain_result,
                alternatives
            )
            self.__overview.add(self.explain_alternatives_object, text='Explain position in rank')
        else:
            self.__logger('Result is none', Severity.ERROR)

    def __save_model(self):
        if self.__ror_result is None or self.__ror_parameters is None:
            self.__logger('Data is none, failed to save model', Severity.ERROR)
            return
        save_model(
            self.__ror_result.model.dataset,
            self.__ror_parameters,
            f'{self.__ror_result.results_aggregator.name}_result',
            self.__logger)

    def close_window(self):
        if self.__results_data is not None:
            self.__results_data.destroy()
            self.__results_data = None
        if self.__close_callback is not None:
            self.__close_callback(self.master)
        self.destroy()
