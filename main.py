import tkinter as tk
from tkinter import StringVar, ttk
from typing import Dict, List, Tuple
import os.path as path
import os

from ror.Dataset import RORDataset
from ror.dataset_constants import CRITERION_TYPES
from ror.CalculationsException import CalculationsException
from ror.RORParameters import RORParameters
from ror.data_loader import RORParameter
from utils.AggregationWidget import AggregationWidget
from utils.AlphaValuesFrame import AlphaValuesFrame
from utils.DataTab import DataTab
from utils.PreferenceIntensityRelationsFrame import PreferenceIntensityRelationsFrame
from utils.ScrollableFrame import ScrollableFrame
from utils.tk.BordaAggregatorOptionsDialog import BordaCopelandAggregatorOptionsDialog, BordaCopelandAggregatorOptionsDialogResult
from utils.tk.DefaultAggregatorOptionsDialog import DefaultAggregatorOptionsDialog, DefaultAggregatorOptionsDialogResult
from utils.tk.WeightedAggregatorOptionsDialog import WeightedAggregatorOptionsDialog, WeightedAggregatorOptionsDialogResult
from utils.PreferenceRelationsFrame import PreferenceRelationsFrame
from utils.ResultWindow import ResultWindow
from utils.Severity import Severity
from utils.solver_helpers import solve_problem
from utils.tk.ScrolledText import ScrolledText
from utils.time import get_log_time
from utils.file_handler import get_file, open_file
from datetime import datetime
from ttkthemes import ThemedStyle
import logging

from utils.tk.io_helper import save_model


class RORWindow:
    def __init__(self) -> None:
        self.root: tk.Tk = tk.Tk()
        # set style as early as possible
        style = ThemedStyle(self.root)
        style.set_theme('radiance') #clearlooks, equilux, arc

        self.simulation_text = tk.StringVar()
        self.log_console: ScrolledText = None
        self.table: DataTab = None
        self.root_frames: Dict[str, ttk.Frame] = dict()
        self.open_default_file_button: ttk.Button = None
        self.debug: bool = True
        self.current_filename: str = None
        self.dataset: RORDataset = None
        self.parameters: RORParameters = None
        self.result_windows: dict[tk.Frame, ResultWindow] = dict()
        self.alpha_values_list: AlphaValuesFrame = None
        self.epsilion_value: tk.StringVar = StringVar()
        self.aggregation_method: AggregationWidget = None
        self.information_box: tk.Frame = None
        self.main_tab: ttk.Notebook = None
        self.example_files_list: ttk.Frame = None
        self.init_gui()

    def open_file(self, filename: str):
        try:
            loading_result = open_file(filename)
            # close old file
            self.close_file()
            # open new file
            self.dataset = loading_result.dataset
            self.parameters = loading_result.parameters
            self.table.set_data(
                self.dataset,
                self.parameters.get_parameter(RORParameter.PRECISION)
            )
            self.current_filename = filename
            self.log(f'Opened file {filename}', Severity.SUCCESS)
            self.show_information_tab()
        except Exception as e:
            self.current_filename = None
            self.log(f"Failed to read file. Exception {e}", Severity.ERROR)
            raise e

    def open_file_dialog(self):
        try:
            filename = get_file()
        except Exception as e:
            self.current_filename = None
            self.log(f"Failed to get file. Exception {e}", Severity.ERROR)
        if filename == '':
            self.current_filename = None
            self.log('No file selected', Severity.WARNING)
        else:
            self.open_file(filename)

    def save_file(self):
        if self.dataset is None:
            self.log('Dataset is empty', Severity.ERROR)
            return

        if not self.validate_model():
            self.log('Failed to save model, model is not valid', Severity.ERROR)
            return
        
        save_model(self.root, self.dataset, self.parameters, self.current_filename, self.log)

    def close_file(self):
        self.table.clean_data()
        self.dataset = None
        if self.current_filename is not None and self.current_filename != '':
            self.log(f'Closed file {self.current_filename}')
        self.current_filename = None
        self.parameters = None
        self.alpha_values_list = None
        self.hide_information_tab()

    def cancel_changes(self):
        if self.current_filename is not None:
            self.open_file(self.current_filename)
            self.log(
                f'Canceled changes - reopened file {self.current_filename}', Severity.SUCCESS)
        else:
            self.log('No file is currently opened', Severity.WARNING)

    def validate_model(self) -> bool:
        if self.parameters is None:
            self.log('parameters object is None', Severity.ERROR)
            return False

        parameters_are_valid = True
        is_epsilion_valid, new_epsilion = self.try_to_validate_epsilion_value()
        if is_epsilion_valid:
            self.parameters.add_parameter(RORParameter.EPS, new_epsilion)
        parameters_are_valid = is_epsilion_valid

        try:
            aggregation_method_name = self.aggregation_method.get_aggregation_method_name()
            self.parameters.add_parameter(RORParameter.RESULTS_AGGREGATOR, aggregation_method_name)
        except:
            self.log('Failed to get aggregation method', Severity.ERROR)
            parameters_are_valid = False
        return parameters_are_valid

    def init_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        filemenu = tk.Menu(menu)
        filemenu.add_command(
            label="Open file...", command=self.open_file_dialog, accelerator="Control+O")
        save_file_menu = tk.Menu(filemenu)
        save_file_menu.add_command(
            label="Save to ror file (data with preferences)", command=lambda: self.save_file())
        filemenu.add_cascade(label="Save...", menu=save_file_menu)
        menu.add_cascade(label="File", menu=filemenu)

        log = tk.Menu(menu)
        menu.add_cascade(label="Log", menu=log)
        log.add_command(
            label='Clear log', command=lambda: self.log_console.clear(), accelerator="F1")

    def init_gui(self):
        self.root.columnconfigure(0, weight=9)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=1)
        screen_width = int(self.root.winfo_screenwidth()*.8)
        screen_height = int(self.root.winfo_screenheight()*.8)
        logging.info(f"Setting scrren to (w x h): {screen_width}x{screen_height}")
        self.root.minsize(screen_width, screen_height)
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.title('ROR')

        self.main_tab = ttk.Notebook(self.root)
        self.main_tab.grid(row=0, column=0, sticky=tk.NSEW)
        self.table = DataTab(self.main_tab)
        self.main_tab.add(self.table, text='Data')

        # log_console
        log_console_frame = ttk.Frame(self.root, padding=2)
        log_console_columnspan = 1 if self.debug else 2
        log_console_frame.grid(
            column=0, row=1, columnspan=log_console_columnspan, sticky=tk.NSEW)
        log_console_frame.rowconfigure(0, weight=1)
        log_console_frame.rowconfigure(1, weight=8)
        self.root_frames['log_console'] = log_console_frame
        ttk.Label(log_console_frame, text='Log window')\
            .grid(row=0, column=0, sticky=(tk.NSEW))
        self.log_console = ScrolledText(self.root,
            log_console_frame, height=10, state=tk.DISABLED)
        # update grid for log console
        self.log_console.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        # by default set information box with no file opened
        self.hide_information_tab()

        # prepare menu
        self.init_menu()

        self.display_list_with_example_files()
        # uncomment to read example file at program startup and solve it
        # self.open_file(self.get_example_files()[0][1])
        # self.solve()

    def get_example_files(self) -> List[str]:
        root_dir = os.path.dirname(os.path.realpath(__file__))
        example_files_root_dir = 'example_problems'
        directory = os.path.join(root_dir, example_files_root_dir)
        problem_file_extension = 'txt'
        example_files: List[str] = []
        if not os.path.exists(directory):
            self.log(f'Failed to list example files. Directory with example files {directory} doesn\'t exist', Severity.WARNING)
            return []
        else:
            files = os.listdir(directory)
            for file in files:
                if file.endswith(f'.{problem_file_extension}'):
                    example_files.append((file, os.path.join(directory, file)))
        if len(example_files) < 1:
            self.log(f'Found no files with example problem in dir {directory}', Severity.WARNING)
        else:
            self.log(f'Found {len(example_files)} file(s) with example problem in dir {directory}')
        return example_files

    def display_list_with_example_files(self):
        self.example_files_list = ttk.Frame(self.root)
        self.example_files_list.grid(column=1, row=1, sticky=tk.NSEW)
        ttk.Label(self.example_files_list, text='Example files with problems')\
            .pack(anchor=tk.NW, fill=tk.X)
        example_files: List[str] = self.get_example_files()
        if len(example_files) < 1:
            ttk.Label(self.example_files_list, text='No files found', font=('Arial', 10), foreground='red3')\
                .pack(anchor=tk.NW, fill=tk.X)
        else:
            weights_frame = ttk.Frame(self.example_files_list)
            weights_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            scroll = ScrollableFrame(weights_frame)
            scroll.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            # create all items
            for idx, (file, file_path) in enumerate(example_files):
                fr = ttk.Frame(scroll.frame, padding=5)
                fr.rowconfigure(0, weight=2)
                fr.rowconfigure(1, weight=1)
                fr.columnconfigure(0, weight=7)
                fr.columnconfigure(1, weight=3)
                fr.pack(anchor=tk.NW, fill=tk.X, expand=1)
                ttk.Label(fr, text=f'{idx+1}. Name: {file}').\
                    grid(row=0, column=0, sticky=tk.W)
                ttk.Label(fr, text=f'Path: {file_path}', font=('Arial', 10), wraplength=200).\
                    grid(row=1, column=0, sticky=tk.W)
                from functools import partial
                ttk.Button(fr, text='Open', command=partial(self.open_file, file_path)).\
                    grid(row=0, column=1, rowspan=2, sticky=tk.E)

    def clear_log(self):
        self.log_console.clear()

    def __run_solver(self, dataset: RORDataset, parameters: RORParameters):
        tab = ttk.Frame(self.main_tab)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        self.main_tab.add(
            tab, text=f'Result {now_str}, {self.current_filename.split(path.sep)[-1]}')
        last_tab_id = len(self.main_tab.tabs())-1
        # focus on the last tab
        self.main_tab.select(last_tab_id)
        self.result_windows[tab] = ResultWindow(
            self.log,
            self.root,
            dataset,
            parameters,
            tab,
            self.on_result_close,
        )
        try:
            result = solve_problem(
                dataset,
                parameters,
                self.log,
                self.result_windows[tab].report_progress,
                parameters.get_parameter(RORParameter.RESULTS_AGGREGATOR)
            )
            self.result_windows[tab].set_result(result, dataset.alternatives, parameters)
        except CalculationsException as e:
            self.log(f'Failed to finish calculations: {e}', Severity.ERROR)
        except Exception as e:
            self.log(f'Failed to solve problem: {e}', Severity.ERROR)
            raise e

    def solve(self):
        if not self.validate_model():
            self.log('Failed to solve model, model is not valid', Severity.ERROR)
            return

        def on_weighted_window_parameters_set(parameters: WeightedAggregatorOptionsDialogResult):
            try:
                alpha_with_weights, resolver = parameters
                weights: List[float] = [item.weight for item in alpha_with_weights]
                alpha_values: List[float] = [item.alpha_value for item in alpha_with_weights]
                new_parameters = self.parameters.deep_copy()
                
                new_parameters.add_parameter(RORParameter.ALPHA_WEIGHTS, weights)
                new_parameters.add_parameter(RORParameter.NUMBER_OF_ALPHA_VALUES, len(alpha_values))
                new_parameters.add_parameter(RORParameter.ALPHA_VALUES, alpha_values)
                new_parameters.add_parameter(RORParameter.TIE_RESOLVER, resolver)
                alpha_with_weights = ', '.join(
                    [f'<alpha: {i.alpha_value}, weight: {i.weight}>' for i in alpha_with_weights]
                )
                self.log(f'Setting alpha values with weights {alpha_with_weights}')
                # create a deep copy of dataset and parameters so next runs are not affected by changes in those
                # variables
                self.__run_solver(self.dataset.deep_copy(), new_parameters)
            except Exception as e:
                self.log(f'Failed to run solver with weighted aggregator: {e}', Severity.ERROR)
                raise e

        def on_borda_copeland_window_parameters_set(parameters: BordaCopelandAggregatorOptionsDialogResult):
            try:
                alpha_values_count, voting_method_name = parameters
                new_parameters = self.parameters.deep_copy()
                new_parameters.add_parameter(RORParameter.NUMBER_OF_ALPHA_VALUES, alpha_values_count)
                self.log(f'Running {voting_method_name} aggregator with {alpha_values_count} alpha values.')
                # create a deep copy of dataset and parameters so next runs are not affected by changes in those
                # variables
                self.__run_solver(self.dataset.deep_copy(), new_parameters)
            except Exception as e:
                self.log(f'Failed to run solver with {voting_method_name} aggregator: {e}', Severity.ERROR)
        
        def on_default_window_parameters_set(parameters: DefaultAggregatorOptionsDialogResult):
            try:
                resolver = parameters
                new_parameters = self.parameters.deep_copy()
                new_parameters.add_parameter(RORParameter.TIE_RESOLVER, resolver)
                self.log(f'Running Default aggregator with {resolver} resolver.')
                self.__run_solver(self.dataset.deep_copy(), new_parameters)
            except Exception as e:
                self.log(f'Failed to run solver with default aggregator: {e}', Severity.ERROR)

        method_name = self.parameters.get_parameter(RORParameter.RESULTS_AGGREGATOR)
        if method_name == 'WeightedResultAggregator':
            try:
                weights = self.parameters.get_parameter(RORParameter.ALPHA_WEIGHTS)
                alpha_values = self.parameters.get_parameter(RORParameter.ALPHA_VALUES)
                WeightedAggregatorOptionsDialog(
                    self.root,
                    'Add parameters for weighted aggregator',
                    on_submit_callback=on_weighted_window_parameters_set,
                    submit_button_text='Solve',
                    weights=weights,
                    alpha_values=alpha_values
                )
            except Exception as e:
                self.log(f'Failed to use weighted aggregator, error: {e}', Severity.ERROR)
        elif method_name in ['BordaResultAggregator', 'CopelandResultAggregator']:
            voting_method_name = 'Borda' if method_name == 'BordaResultAggregator' else 'Copeland'
            try:
                BordaCopelandAggregatorOptionsDialog(
                    self.root,
                    f'Add parameters for {voting_method_name} aggregator',
                    voting_method_name,
                    on_submit_callback=on_borda_copeland_window_parameters_set
                )
            except Exception as e:
                self.log(f'Failed to use {voting_method_name} aggregator, error: {e}', Severity.ERROR)
        elif method_name == 'DefaultResultAggregator':
            try:
                DefaultAggregatorOptionsDialog(
                    self.root,
                    'Add parameters for Default aggregator',
                    on_submit_callback=on_default_window_parameters_set
                )
            except Exception as e:
                self.log(f'Failed to use default aggregator, error: {e}', Severity.ERROR)
        else:
            # create a deep copy of dataset and parameters so next runs are not affected by changes in those
            # variables
            self.__run_solver(self.dataset.deep_copy(), self.parameters.deep_copy())

    def on_result_close(self, tab_frame: ttk.Frame):
        self.result_windows[tab_frame].master.destroy()
        del self.result_windows[tab_frame]
    '''
    Returns information box that consumes 80% of the height of the information tab
    and information bottom box that takes 10% of the height of the information tab
    '''

    def create_information_tab(self) -> Tuple[ttk.Frame, ttk.Frame]:
        if 'information' in self.root_frames:
            self.root_frames['information'].destroy()
        information_frame = ttk.Frame(self.root, padding=2)
        information_frame.rowconfigure(0, weight=8)
        information_frame.rowconfigure(1, weight=1)
        information_frame.grid(
            column=1, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['information'] = information_frame
        information_box = ScrollableFrame(information_frame)
        information_box.grid(row=0, column=0, sticky=tk.NSEW)
        information_box_bottom = ttk.Frame(information_frame, padding=2)
        information_box_bottom.grid(row=1, column=0, sticky=tk.NSEW)
        return information_box.frame, information_box_bottom

    def try_to_validate_epsilion_value(self) -> Tuple[bool, float]:
        new_value = self.epsilion_value.get()
        float_value: float = 0.0
        try:
            float_value = float(new_value)
            if float_value < 0.0:
                self.log('Epsilion value cannot be lower than 0', Severity.ERROR)
                return (False, None)
            return (True, float_value)
        except:
            self.log(f'Failed set epsilion value. Failed to parse float value from {new_value}', Severity.ERROR)
            return (False, None)

    def show_information_tab(self):
        if self.dataset is None:
            self.log('No dataset available', Severity.ERROR)
        if self.current_filename is None or self.current_filename == '':
            self.log('Filename is invalid', Severity.ERROR)
        filename = self.current_filename
        # information frame
        information_box, information_box_bottom = self.create_information_tab()
        self.information_box = information_box
        ttk.Label(information_box, text='Information about opened file').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text='Filename: ').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=filename).pack(anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        self.epsilion_value.set(self.parameters.get_parameter(RORParameter.EPS))
        ttk.Label(information_box, text=f'Epsilon value:').pack(anchor=tk.N, fill=tk.X)
        name_entry = ttk.Entry(information_box, textvariable=self.epsilion_value,width=10)
        name_entry.pack(anchor=tk.NW)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        precision = self.parameters.get_parameter(RORParameter.PRECISION)
        ttk.Label(information_box, text=f'Display precision: {precision}').pack(anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Number of alternatives: {len(self.dataset.alternatives)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Number of criteria: {len(self.dataset.criteria)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Criteria:').pack(
            anchor=tk.N, fill=tk.X)
        for index, (criterion_name, criterion_type) in enumerate(self.dataset.criteria):
            type_name = 'cost' if criterion_type == CRITERION_TYPES['cost'] else 'gain'
            ttk.Label(
                information_box, text=f'{index+1}. {criterion_name}, type: {type_name}').pack(anchor=tk.N, fill=tk.X)
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Alpha values:').pack(
            anchor=tk.N, fill=tk.X)
        alpha_values_box = tk.Frame(information_box)
        alpha_values_box.pack(anchor=tk.NW, fill=tk.X)
        scrollbar = tk.Scrollbar(alpha_values_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.alpha_values_list = tk.Listbox(alpha_values_box, height=5, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.alpha_values_list.yview)
        self.alpha_values_list.pack(anchor=tk.N, fill=tk.X)
        for index, alpha_value in enumerate(self.parameters.get_parameter(RORParameter.ALPHA_VALUES)):
            self.alpha_values_list.insert(index, f'{index+1}. Alpha value: {alpha_value}')

        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Relations').pack(
            anchor=tk.N, fill=tk.X)
        tab_control = ttk.Notebook(information_box)
        preference_relations_tab = ttk.Frame(tab_control)
        intensity_relations_tab = ttk.Frame(tab_control)

        tab_control.add(preference_relations_tab, text='Preference relations')
        tab_control.add(intensity_relations_tab, text='Intensity relations')
        tab_control.pack(anchor=tk.N, fill=tk.BOTH)

        preference_frame = PreferenceRelationsFrame(preference_relations_tab, self.dataset, True, self.log)
        preference_frame.pack(anchor=tk.N, fill=tk.X)

        preference_intensity_frame = PreferenceIntensityRelationsFrame(intensity_relations_tab, self.dataset, True, self.log)
        preference_intensity_frame.pack(anchor=tk.N, fill=tk.X)
        
        ttk.Separator(information_box, orient='horizontal').pack(fill='x')
        ttk.Label(information_box, text=f'Aggregation method').pack(
            anchor=tk.N, fill=tk.X)
        self.aggregation_method = AggregationWidget(
            information_box,
            self.parameters.get_parameter(RORParameter.RESULTS_AGGREGATOR)
        )

        # bottom tab buttons
        information_box_bottom.columnconfigure(0, weight=1)
        information_box_bottom.columnconfigure(1, weight=1)
        information_box_bottom.columnconfigure(2, weight=1)
        information_box_bottom.columnconfigure(3, weight=1)
        information_box_bottom.rowconfigure(0, weight=1)
        ttk.Button(
            master=information_box_bottom,
            text='Solve',
            command=lambda: self.solve()
        ).grid(column=0, row=0)
        ttk.Button(
            master=information_box_bottom,
            text='Save file',
            command=lambda: self.save_file()
        ).grid(column=1, row=0)
        ttk.Button(
            master=information_box_bottom,
            text='Cancel changes',
            command=lambda: self.cancel_changes()
        ).grid(column=2, row=0)
        ttk.Button(
            master=information_box_bottom,
            text='Close file',
            command=lambda: self.close_file()
        ).grid(column=3, row=0)

    def hide_information_tab(self):
        information_box, information_box_bottom = self.create_information_tab()
        ttk.Label(information_box, text='No file is opened').pack(
            anchor=tk.N, fill=tk.X)
        # bottom tab buttons
        information_box_bottom.columnconfigure(0, weight=1)
        information_box_bottom.rowconfigure(0, weight=1)
        ttk.Button(
            master=information_box_bottom,
            text='Open file',
            command=lambda: self.open_file_dialog()
        ).grid(column=0, row=0)

    def log(self, message: str, severity: Severity = Severity.INFO):
        '''
        Logs message to a console with specified severity.
        '''
        if self.log_console is None:
            return
        data = f'[{get_log_time()}][{severity.value}]: {message}\n'
        color = None
        if severity == Severity.ERROR:
            color = 'red3'
        elif severity == Severity.WARNING:
            color = 'DarkOrange2'
        elif severity == Severity.SUCCESS:
            color = 'forest green'
        self.log_console.add_text(data, color)

    def run(self):
        self.root.mainloop()


def main():
    RORWindow().run()


if __name__ == '__main__':
    main()
