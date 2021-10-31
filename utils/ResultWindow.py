from math import floor
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, asksaveasfilename
from typing import Callable, List, Tuple
from ror.Dataset import RORDataset
from ror.RORParameters import RORParameters
from ror.RORResult import RORResult
from ror.BordaTieResolver import BordaTieResolver
from ror.CopelandTieResolver import CopelandTieResolver
from ror.NoTieResolver import NoTieResolver
from ror.loader_utils import RORParameter
from ror.ror_solver import ProcessingCallbackData
from utils.ExplainAlternatives import ExplainAlternatives
from utils.PreferenceRelationsFrame import PreferenceRelationsFrame
from utils.PreferenceIntensityRelationsFrame import PreferenceIntensityRelationsFrame
from ror.DefaultResultAggregator import DefaultResultAggregator
from ror.WeightedResultAggregator import WeightedResultAggregator
from ror.BordaResultAggregator import BordaResultAggregator
from ror.CopelandResultAggregator import CopelandResultAggregator

from utils.ProgressBar import ProgressBar
from utils.Table import Table
from utils.image_helper import ImageDisplay
from utils.Severity import Severity
from utils.tk.BordaVotingResult import BordaVotingResult
from utils.tk.CopelandVotingResult import CopelandVotingResult
from utils.tk.io_helper import save_model, save_model_latex
from utils.type_aliases import LoggerFunc


class ResultWindow(ttk.Frame):
    def __init__(
            self,
            logger: LoggerFunc,
            window_object: tk.Tk,
            dataset: RORDataset,
            parameters: RORParameters,
            root: tk.Tk,
            close_callback: Callable[[tk.Frame], None] = None):
        ttk.Frame.__init__(self, master=root)
        self.__logger: LoggerFunc = logger
        self.__window_object: tk.Tk = window_object
        self.__progress_bar: ProgressBar = None
        self.__results_data: Table = None
        self.__solution_properties_tab: tk.Frame = None
        self.__close_callback = close_callback
        self.top_frame: ttk.Frame = None
        self.ranks_tab: ttk.Notebook = None
        self.final_image_frame: tk.Frame = None
        self.__overview: ttk.Notebook = None
        self.__ror_result: RORResult = None
        self.__ror_parameters: RORParameters = parameters
        self.__ror_dataset: RORDataset = dataset
        self.__image_count: int = 1
        self.explain_alternatives_object: ExplainAlternatives = None
        self.init_gui()

    def init_gui(self):
        self.rowconfigure(0, weight=9)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.__progress_bar = ProgressBar(self)
        self.__progress_bar.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=tk.N, pady=50)
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
        if data.progress < 0:
            root = ttk.Frame(self)
            # processing error
            ttk.Label(root, text='Failed to calculate solution from provided data', font=('Arial', 17), foreground='red3').\
                pack(anchor=tk.NW)
            cause = data.status if data.status is not None and data.status else 'unknown'
            ttk.Label(root, text=f'cause: {cause}', font=('Arial', 14)).\
                pack(anchor=tk.NW)
            if self.__ror_parameters is None:
                ttk.Label(root, text=f'Parameters were not provided', font=('Arial', 14)).\
                    pack(anchor=tk.NW)
            else:
                parameters = self.__display_model_parameters(
                    root,
                    self.__ror_parameters
                )
                parameters.pack(anchor=tk.NW, fill=tk.X, expand=1)
            parameters.pack(anchor=tk.NW)
            if self.__ror_dataset is None:
                ttk.Label(root, text=f'Dataset was not provided', font=('Arial', 14)).\
                    pack(anchor=tk.NW)
            else:
                preferences = self.__display_model_preferences(
                    root,
                    self.__ror_dataset
                )
                preferences.pack(anchor=tk.NW, fill=tk.X, expand=1)
            root.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=tk.N)
        else:
            self.__set_progress(floor(data.progress*100), data.status)
        self.update()

    def __add_image(self, image: ImageDisplay, name: str = None):
        self.ranks_tab.add(
            image,
            text=name if name is not None else str(self.__image_count),
            compound=tk.TOP,
            sticky=tk.NSEW,
            underline=2
        )
        self.__image_count += 1

    def __display_model_parameters(self, root: ttk.Frame, parameters: RORParameters) -> tk.Frame:
        frame = ttk.Frame(root)
        ttk.Label(frame, text='Parameters', font=('Arial', 17)).pack(anchor=tk.NW)
        method_parameters: List[Tuple[str, str]] = []
        precision = parameters.get_parameter(RORParameter.PRECISION)
        for parameter in RORParameter:
            if parameter in [RORParameter.ALPHA_VALUES, RORParameter.ALPHA_WEIGHTS]:
                rounded_values = [round(value, precision) for value in parameters.get_parameter(parameter)]
                method_parameters.append((parameter.value, rounded_values))
            else:
                method_parameters.append((parameter.value, parameters.get_parameter(parameter)))
        parameters_table = Table(frame)
        parameters_table.set_simple_data(method_parameters)
        parameters_table.pack(anchor=tk.NW, fill=tk.X, expand=0)
        return frame

    def __display_model_preferences(
        self,
        root: tk.Frame,
        dataset: RORDataset
    ) -> tk.Frame:
        preferences_frame = ttk.Frame(root)
        ttk.Label(preferences_frame, text='Preference relations', font=('Arial', 17)).pack(anchor=tk.NW)
        preferences_windows = ttk.Frame(preferences_frame)
        preferences_windows.rowconfigure(0, weight=1)
        preferences_windows.columnconfigure(0, weight=1)
        preferences_windows.columnconfigure(1, weight=1)
        preferences_windows.pack(anchor=tk.NW, fill=tk.X, expand=1)
        preferences = PreferenceRelationsFrame(preferences_windows, dataset, False, self.__logger)
        preferences.grid(row=0, column=0, sticky=tk.NSEW)
        intensity_preferences = PreferenceIntensityRelationsFrame(preferences_windows, dataset, False, self.__logger)
        intensity_preferences.grid(row=0, column=1, sticky=tk.NSEW)
        return preferences_frame

    def save_data(self, type: str):
        if type not in ['csv', 'tex']:
            self.__logger(f'Type {type} is not handled')
            return
        _filename = asksaveasfilename(
            defaultextension=f".{type}",
            title="Save dataset"
        )
            
        if _filename is None or _filename == '':
            self.__logger('Cancelled file saving')
            return
        try:
            if type == 'tex':
                result = self.__ror_result.save_result_to_latex(_filename)
            else:
                result = self.__ror_result.save_result_to_csv(_filename)
        except Exception as e:
            self.__logger(f'Failed to save file, error: {e}', Severity.ERROR)
            return
        self.__logger(f'Saved file as {result}')

    def __pick_directory(self) -> None:
        if self.__ror_result is None:
            self.__logger(f'Failed to save tie resolver data - ROR result is None', Severity.ERROR)
            return None
        _dir = askdirectory(mustexist=False)
        if _dir is None or _dir == '':
            self.__logger(f'Failed to save tie resolver data - directory is invalid', Severity.ERROR)
            return None
        return _dir

    def save_tie_resolver_data(self):
        _dir = self.__pick_directory()
        if _dir is None:
            return
        result = self.__ror_result.save_tie_resolvers_data(_dir)
        if result is None:
            self.__logger(f'Failed to save tie resolver data - no data was available', Severity.ERROR)
        else:
            self.__logger(f'Saved tie resolver data to: {", ".join(result)}')

    def save_voting_data(self, save_voting_data_func: Callable[[str], List[str]]):
        _dir = self.__pick_directory()
        if _dir is None:
            return
        result = save_voting_data_func(_dir)
        if result is None:
            self.__logger(f'Failed to save voting data - no data was available', Severity.ERROR)
        else:
            self.__logger(f'Saved voting data to: {", ".join(result)}')

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
            self.__add_image(final_image, name='final')

            self.ranks_tab.select(0)
            details_frame = ttk.Frame(self)
            details_frame.grid(row=0, column=0, sticky=tk.NSEW)

            # overview notebook
            self.__overview = ttk.Notebook(details_frame)
            self.__overview.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)

            data_tab = ttk.Frame(self.__overview)
            data_tab.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            self.__overview.add(data_tab, text='Calculated distances')

            self.__results_data = Table(data_tab)
            ttk.Label(data_tab, text='Distances from alternatives to reference alternative calculated by solving the problem with ROR-distance method')\
                .pack(anchor=tk.NW)
            self.__results_data.set_alternatives_pandas_data(
                result.get_result_table(),
                display_precision=parameters.get_parameter(RORParameter.PRECISION)
            )
            self.__results_data.pack(anchor=tk.N, fill=tk.BOTH, expand=1)
            frame = ttk.Frame(data_tab)
            frame.pack(anchor=tk.N, fill=tk.X, expand=1)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            ttk.Button(frame, text='Save result to csv file', padding=10, command=lambda: self.save_data('csv'))\
                .grid(row=0, column=0, sticky=tk.E)
            ttk.Button(frame, text='Save result to latex file', padding=10, command=lambda: self.save_data('tex'))\
                .grid(row=0, column=1, sticky=tk.W)

            self.__solution_properties_tab = ttk.Frame(self.__overview)
            self.__overview.add(self.__solution_properties_tab, text='Model properties')

            self.__solution_properties_tab.rowconfigure(0, weight=1)
            self.__solution_properties_tab.rowconfigure(1, weight=1)
            self.__solution_properties_tab.rowconfigure(2, weight=1)
            
            # parameters
            parameters_frame: ttk.Frame = self.__display_model_parameters(self.__solution_properties_tab, result.parameters)
            parameters_frame.grid(row=0, sticky=tk.NSEW)

            # add preference relations
            preferences_frame: ttk.Frame = self.__display_model_preferences(self.__solution_properties_tab, result.model.dataset)
            preferences_frame.grid(row=1, sticky=tk.NSEW)

            buttons = ttk.Frame(self.__solution_properties_tab)
            # buttons.pack(anchor=tk.NW)
            buttons.grid(row=2, sticky=tk.EW)
            buttons.rowconfigure(0, weight=1)
            for col in range(4):
                buttons.columnconfigure(col, weight=1)
            ttk.Button(
                buttons,
                text='Save problem',
                command=lambda: self.__save_model()
            ).grid(row=0, column=1, sticky=tk.NSEW)
            ttk.Button(
                buttons,
                text='Save constraints to latex',
                command=lambda: self.__save_model_to_tex()
            ).grid(row=0, column=2, sticky=tk.NSEW)

            # explain result frame
            self.explain_alternatives_object = ExplainAlternatives(
                self,
                result.results_aggregator.explain_result,
                alternatives
            )
            self.__overview.add(self.explain_alternatives_object, text='Explain position in rank')

            tie_resolver = result.results_aggregator.tie_resolver
            if tie_resolver is not None and not isinstance(tie_resolver, NoTieResolver):
                tie_resolver_frame = ttk.Frame(self.__overview)
                tie_resolver_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                self.__overview.add(tie_resolver_frame, text='Tie resolver result')
                invalid_resolver = False
                if isinstance(tie_resolver, BordaTieResolver):
                    # display
                    borda_voter = tie_resolver.voter
                    BordaVotingResult(tie_resolver_frame, borda_voter, result.parameters)\
                        .pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                elif isinstance(tie_resolver, CopelandTieResolver):
                    copeland_voter = tie_resolver.voter
                    CopelandVotingResult(tie_resolver_frame, copeland_voter, result.model.dataset, result.parameters)\
                        .pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                else:
                    invalid_resolver = True
                    ttk.Label(tie_resolver_frame, text='Unknown tie resolver provided', foreground='red3')
                    self.__logger('Unknown tie resolver provided')
                if not invalid_resolver:
                    # common for both resolvers
                    from functools import partial
                    ttk.Button(
                        tie_resolver_frame,
                        text='Save tie resolver data',
                        command=self.save_tie_resolver_data
                    ).pack(anchor=tk.NW)

            if result.results_aggregator is not None and not isinstance(result.results_aggregator, (DefaultResultAggregator, WeightedResultAggregator)):
                result_aggregator_data_frame = ttk.Frame(self.__overview)
                result_aggregator_data_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                self.__overview.add(result_aggregator_data_frame, text='Voting data')
                save_votes_func: Callable[[str], List[str]] = None
                if isinstance(result.results_aggregator, BordaResultAggregator):
                    # display
                    BordaVotingResult(result_aggregator_data_frame, result.results_aggregator.voter, result.parameters)\
                        .pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                    save_votes_func = result.results_aggregator.voter.save_voting_data
                elif isinstance(result.results_aggregator, CopelandResultAggregator):
                    CopelandVotingResult(result_aggregator_data_frame, result.results_aggregator.voter, result.model.dataset, result.parameters)\
                        .pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                    save_votes_func = result.results_aggregator.voter.save_voting_data
                else:
                    ttk.Label(result_aggregator_data_frame, text='Unknown result aggregator provided', foreground='red3')
                    self.__logger('Unknown result aggregator provided')
                if save_votes_func is not None:
                    # common for both resolvers
                    from functools import partial
                    ttk.Button(
                        result_aggregator_data_frame,
                        text='Save voting data',
                        command=partial(self.save_voting_data, save_votes_func)
                    ).pack(anchor=tk.NW)
        else:
            self.__logger('Result is none', Severity.ERROR)

    def __save_model(self):
        if self.__ror_result is None or self.__ror_parameters is None:
            self.__logger('Data is none, failed to save model', Severity.ERROR)
            return
        save_model(
            self,
            self.__ror_result.model.dataset,
            self.__ror_parameters,
            f'{self.__ror_result.results_aggregator.name}_result',
            self.__logger
        )
    
    def __save_model_to_tex(self):
        if self.__ror_result is None or self.__ror_parameters is None:
            self.__logger('Data is none, failed to save model', Severity.ERROR)
            return
        save_model_latex(
            self,
            self.__ror_result.model,
            self.__ror_parameters,
            f'{self.__ror_result.results_aggregator.name}_result',
            self.__logger
        )

    def close_window(self):
        if self.__results_data is not None:
            self.__results_data.destroy()
            self.__results_data = None
        if self.__close_callback is not None:
            self.__close_callback(self.master)
        self.destroy()
